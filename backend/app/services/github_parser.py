"""
GitHub 项目解析服务
自动从 GitHub URL 提取项目信息
"""

import re
import httpx
from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass

from app.core.logging import logger


@dataclass
class GitHubProjectInfo:
    """GitHub 项目信息"""

    name: str
    full_name: str
    description: str
    url: str
    stars: int
    forks: int
    language: Optional[str]
    topics: List[str]
    readme_content: str
    readme_summary: Optional[str]
    last_updated: datetime
    is_private: bool


class GitHubParser:
    """GitHub 项目解析器"""

    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token
        self.base_url = "https://api.github.com"
        self.raw_url = "https://raw.githubusercontent.com"

    def _extract_owner_repo(self, github_url: str) -> Optional[tuple]:
        """从 GitHub URL 提取 owner 和 repo"""
        # 支持多种格式：
        # https://github.com/owner/repo
        # https://github.com/owner/repo/
        # github.com/owner/repo
        patterns = [
            r"github\.com/([^/]+)/([^/]+)/?",
            r"github\.com:([^/]+)/([^/]+)/?",
        ]

        for pattern in patterns:
            match = re.search(pattern, github_url)
            if match:
                owner, repo = match.groups()
                # 移除 .git 后缀
                repo = repo.replace(".git", "")
                return owner, repo

        return None

    def _get_headers(self) -> dict:
        """获取请求头"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "PitchCube-App",
        }
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        return headers

    async def fetch_repo_info(self, owner: str, repo: str) -> Optional[dict]:
        """获取仓库基本信息"""
        url = f"{self.base_url}/repos/{owner}/{repo}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self._get_headers())

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"Repository not found: {owner}/{repo}")
                    return None
                else:
                    logger.error(f"GitHub API error: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Failed to fetch repo info: {e}")
            return None

    async def fetch_readme(self, owner: str, repo: str) -> Optional[str]:
        """获取 README 内容"""
        # 尝试获取 README.md
        urls = [
            f"{self.raw_url}/{owner}/{repo}/main/README.md",
            f"{self.raw_url}/{owner}/{repo}/master/README.md",
            f"{self.base_url}/repos/{owner}/{repo}/readme",
        ]

        for url in urls:
            try:
                async with httpx.AsyncClient() as client:
                    headers = self._get_headers()
                    response = await client.get(url, headers=headers, timeout=10.0)

                    if response.status_code == 200:
                        # 如果是 API 返回的 JSON，提取 content
                        if "api.github.com" in url:
                            data = response.json()
                            import base64

                            content = base64.b64decode(data.get("content", "")).decode(
                                "utf-8"
                            )
                            return content
                        else:
                            return response.text

            except Exception as e:
                logger.warning(f"Failed to fetch README from {url}: {e}")
                continue

        return None

    def _extract_summary_from_readme(
        self, readme_content: str, max_length: int = 500
    ) -> str:
        """从 README 提取项目概述"""
        if not readme_content:
            return ""

        # 移除 Markdown 格式
        # 1. 移除代码块
        text = re.sub(r"```[\s\S]*?```", "", readme_content)
        # 2. 移除行内代码
        text = re.sub(r"`[^`]*`", "", text)
        # 3. 移除图片
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
        # 4. 移除链接，保留文本
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
        # 5. 移除 HTML 标签
        text = re.sub(r"<[^>]+>", "", text)
        # 6. 移除标题标记
        text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        # 7. 移除水平线
        text = re.sub(r"^---+$", "", text, flags=re.MULTILINE)

        # 清理空白字符
        text = re.sub(r"\n+", "\n", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        # 提取前 max_length 个字符
        if len(text) > max_length:
            # 尝试在句子边界截断
            truncated = text[:max_length]
            last_period = truncated.rfind(".")
            last_chinese_punctuation = max(
                truncated.rfind("。"), truncated.rfind("！"), truncated.rfind("？")
            )
            last_break = max(last_period, last_chinese_punctuation)

            if last_break > max_length * 0.5:  # 如果找到合适的断点
                truncated = truncated[: last_break + 1]

            text = truncated + "..."

        return text

    def _extract_features_from_readme(self, readme_content: str) -> List[str]:
        """从 README 提取功能特性"""
        features = []

        # 查找 Features 或 功能 部分
        patterns = [
            r"##\s*Features?\s*\n(.*?)(?=##|$)",
            r"##\s*功能\s*\n(.*?)(?=##|$)",
            r"##\s*Key Features?\s*\n(.*?)(?=##|$)",
            r"##\s*主要功能\s*\n(.*?)(?=##|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, readme_content, re.IGNORECASE | re.DOTALL)
            if match:
                features_section = match.group(1)
                # 提取列表项
                feature_items = re.findall(r"[-*]\s*(.+)", features_section)
                features.extend([f.strip() for f in feature_items[:5]])
                break

        return features

    async def parse_github_url(self, github_url: str) -> Optional[GitHubProjectInfo]:
        """
        解析 GitHub URL，获取项目信息

        Args:
            github_url: GitHub 项目 URL

        Returns:
            GitHubProjectInfo 对象，解析失败返回 None
        """
        logger.info(f"Parsing GitHub URL: {github_url}")

        # 提取 owner 和 repo
        owner_repo = self._extract_owner_repo(github_url)
        if not owner_repo:
            logger.error(f"Invalid GitHub URL: {github_url}")
            return None

        owner, repo = owner_repo

        # 并行获取仓库信息和 README
        repo_info, readme_content = await asyncio.gather(
            self.fetch_repo_info(owner, repo),
            self.fetch_readme(owner, repo),
            return_exceptions=True,
        )

        if isinstance(repo_info, Exception) or repo_info is None:
            logger.error(f"Failed to fetch repo info for {owner}/{repo}")
            return None

        if isinstance(readme_content, Exception):
            readme_content = ""

        # 构建项目信息
        readme_summary = self._extract_summary_from_readme(readme_content)

        return GitHubProjectInfo(
            name=repo_info.get("name", repo),
            full_name=repo_info.get("full_name", f"{owner}/{repo}"),
            description=repo_info.get("description") or readme_summary[:200],
            url=repo_info.get("html_url", github_url),
            stars=repo_info.get("stargazers_count", 0),
            forks=repo_info.get("forks_count", 0),
            language=repo_info.get("language"),
            topics=repo_info.get("topics", []),
            readme_content=readme_content or "",
            readme_summary=readme_summary,
            last_updated=datetime.fromisoformat(
                repo_info.get("updated_at", datetime.utcnow().isoformat()).replace(
                    "Z", "+00:00"
                )
            ),
            is_private=repo_info.get("private", False),
        )

    async def get_product_data_for_pitchcube(self, github_url: str) -> Optional[dict]:
        """
        获取适用于 PitchCube 的产品数据

        Returns:
            dict 包含：
            - name: 产品名称
            - description: 产品描述
            - tagline: 标语
            - key_features: 关键功能列表
            - github_url: GitHub 链接
            - tech_stack: 技术栈
        """
        project_info = await self.parse_github_url(github_url)
        if not project_info:
            return None

        # 提取技术栈（从 topics 和 language）
        tech_stack = project_info.topics[:5]
        if project_info.language and project_info.language not in tech_stack:
            tech_stack.insert(0, project_info.language)

        # 提取功能特性
        features = self._extract_features_from_readme(project_info.readme_content)

        # 生成标语（如果没有描述，从名称生成）
        tagline = (
            project_info.description or f"一个基于 {project_info.language} 的开源项目"
        )
        if len(tagline) > 100:
            tagline = tagline[:97] + "..."

        return {
            "name": project_info.name,
            "description": project_info.readme_summary or project_info.description,
            "tagline": tagline,
            "key_features": features or ["开源项目", "持续更新中"],
            "github_url": project_info.url,
            "stars": project_info.stars,
            "forks": project_info.forks,
            "language": project_info.language,
            "tech_stack": tech_stack,
            "topics": project_info.topics,
        }


# 全局解析器实例
github_parser = GitHubParser()


# 便捷函数
async def parse_github_project(github_url: str) -> Optional[dict]:
    """解析 GitHub 项目并返回 PitchCube 可用的数据"""
    return await github_parser.get_product_data_for_pitchcube(github_url)


# 导入 asyncio 用于并行请求
import asyncio
