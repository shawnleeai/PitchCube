"""
视频渲染服务
使用FFmpeg进行视频合成、拼接、字幕添加等操作
"""

import os
import asyncio
import subprocess
from typing import Optional, List, Dict, Any
from pathlib import Path
from app.core.config import settings
from app.core.logging import logger


class VideoComposer:
    """视频合成服务"""

    def __init__(self):
        self.output_dir = Path("generated/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 检查FFmpeg是否可用
        self.ffmpeg_available = self._check_ffmpeg()

        if not self.ffmpeg_available:
            logger.warning(
                "FFmpeg not available. Video rendering will use fallback mode."
            )

    def _check_ffmpeg(self) -> bool:
        """检查FFmpeg是否可用"""
        try:
            result = subprocess.run(
                [settings.FFMPEG_PATH, "-version"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"FFmpeg check failed: {e}")
            return False

    async def create_simple_video(
        self, task_id: str, title: str, scenes: List[Dict[str, Any]], duration: int = 60
    ) -> Dict[str, Any]:
        """
        创建简化版视频（使用FFmpeg或Fallback）

        Args:
            task_id: 任务ID
            title: 视频标题
            scenes: 场景列表
            duration: 视频时长

        Returns:
            视频信息字典
        """
        try:
            if self.ffmpeg_available:
                return await self._create_video_with_ffmpeg(
                    task_id, title, scenes, duration
                )
            else:
                return await self._create_video_fallback(
                    task_id, title, scenes, duration
                )
        except Exception as e:
            logger.error(f"Video creation failed: {e}")
            return await self._create_video_fallback(task_id, title, scenes, duration)

    async def _create_video_with_ffmpeg(
        self, task_id: str, title: str, scenes: List[Dict[str, Any]], duration: int
    ) -> Dict[str, Any]:
        """
        使用FFmpeg创建视频

        Args:
            task_id: 任务ID
            title: 视频标题
            scenes: 场景列表
            duration: 视频时长

        Returns:
            视频信息字典
        """
        output_path = self.output_dir / f"{task_id}.mp4"

        # 创建临时字幕文件
        subtitle_path = self.output_dir / f"{task_id}_subtitles.srt"
        self._create_subtitle_file(subtitle_path, scenes)

        # 使用FFmpeg创建视频
        # 这里使用简单的slide show效果，每个场景持续相等时间
        scene_duration = duration / len(scenes) if scenes else 1

        # 构建FFmpeg命令
        cmd = [
            settings.FFMPEG_PATH,
            "-y",  # 覆盖输出文件
            "-f",
            "lavfi",
            "-i",
            f"color=c=black:s=1280x720:d={scene_duration}",  # 黑色背景
            "-vf",
            f"drawtext=text='{title}':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-r",
            "30",
            str(output_path),
        ]

        # 执行FFmpeg
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                # Fallback to simpler method
                return await self._create_video_fallback(
                    task_id, title, scenes, duration
                )

            # 生成缩略图
            thumbnail_path = self.output_dir / f"{task_id}_thumb.jpg"
            await self._generate_thumbnail(output_path, thumbnail_path)

            return {
                "video_url": f"/download/videos/{task_id}.mp4",
                "thumbnail_url": f"/download/videos/{task_id}_thumb.jpg",
                "duration": duration,
                "resolution": "720p",
                "format": "mp4",
                "size": output_path.stat().st_size if output_path.exists() else 0,
            }

        except Exception as e:
            logger.error(f"FFmpeg execution failed: {e}")
            return await self._create_video_fallback(task_id, title, scenes, duration)

    async def _create_video_fallback(
        self, task_id: str, title: str, scenes: List[Dict[str, Any]], duration: int
    ) -> Dict[str, Any]:
        """
        Fallback方法：创建模拟视频（实际为静态图片）

        在没有FFmpeg或FFmpeg失败时使用

        Args:
            task_id: 任务ID
            title: 视频标题
            scenes: 场景列表
            duration: 视频时长

        Returns:
            视频信息字典
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            logger.error("PIL not available for video fallback")
            return {
                "video_url": None,
                "thumbnail_url": None,
                "duration": duration,
                "resolution": "720p",
                "format": "mp4",
                "size": 0,
                "note": "Fallback mode: PIL not available",
            }

        output_path = self.output_dir / f"{task_id}.mp4"
        thumbnail_path = self.output_dir / f"{task_id}_thumb.jpg"

        try:
            # 创建一个演示用的静态视频帧
            width, height = 1280, 720
            img = Image.new("RGB", (width, height), color="#1a1a2e")
            draw = ImageDraw.Draw(img)

            try:
                # 尝试使用中文字体
                font_large = ImageFont.truetype("fonts/NotoSansCJKsc-Regular.otf", 72)
                font_medium = ImageFont.truetype("fonts/NotoSansCJKsc-Regular.otf", 36)
                font_small = ImageFont.truetype("fonts/NotoSansCJKsc-Regular.otf", 24)
            except:
                # Fallback to default font
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # 绘制标题
            draw.text(
                (width // 2, 150), title, fill="white", font=font_large, anchor="mm"
            )

            # 绘制场景信息
            y_offset = 300
            for i, scene in enumerate(scenes[:4]):  # 最多显示4个场景
                scene_text = f"{i + 1}. {scene.get('subtitle', '')}"
                draw.text(
                    (width // 2, y_offset),
                    scene_text,
                    fill="#a0a0a0",
                    font=font_small,
                    anchor="mm",
                )
                y_offset += 80

            # 绘制底部信息
            draw.text(
                (width // 2, height - 100),
                f"视频时长: {duration}秒",
                fill="#808080",
                font=font_medium,
                anchor="mm",
            )

            # 保存为缩略图
            img.save(thumbnail_path)

            # 创建一个简单的模拟视频（1秒黑色视频）
            # 在实际环境中，这里应该生成真实视频
            # 作为fallback，我们返回缩略图作为视频URL
            logger.warning(f"Using fallback mode for video {task_id}")

            return {
                "video_url": f"/download/videos/{task_id}_thumb.jpg",  # Fallback: 使用图片代替视频
                "thumbnail_url": f"/download/videos/{task_id}_thumb.jpg",
                "duration": duration,
                "resolution": "720p",
                "format": "mp4",
                "size": thumbnail_path.stat().st_size if thumbnail_path.exists() else 0,
                "note": "Fallback mode: Video rendering unavailable",
            }

        except Exception as e:
            logger.error(f"Fallback video creation failed: {e}")
            return {
                "video_url": None,
                "thumbnail_url": None,
                "duration": duration,
                "resolution": "720p",
                "format": "mp4",
                "size": 0,
                "note": "Fallback mode: Creation failed",
            }

    def _create_subtitle_file(self, subtitle_path: Path, scenes: List[Dict[str, Any]]):
        """
        创建SRT字幕文件

        Args:
            subtitle_path: 字幕文件路径
            scenes: 场景列表
        """
        with open(subtitle_path, "w", encoding="utf-8") as f:
            start_time = 0
            for i, scene in enumerate(scenes):
                duration = scene.get("duration", 5)
                end_time = start_time + duration

                # SRT格式时间
                start_str = self._format_srt_time(start_time)
                end_str = self._format_srt_time(end_time)

                subtitle = scene.get("subtitle", scene.get("narration", ""))[:100]

                f.write(f"{i + 1}\n")
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{subtitle}\n\n")

                start_time = end_time

    def _format_srt_time(self, seconds: float) -> str:
        """
        将秒数转换为SRT时间格式

        Args:
            seconds: 秒数

        Returns:
            SRT格式时间字符串，例如 "00:00:01,500"
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    async def _generate_thumbnail(
        self, video_path: Path, thumbnail_path: Path, timestamp: float = 1.0
    ):
        """
        从视频中提取缩略图

        Args:
            video_path: 视频文件路径
            thumbnail_path: 缩略图保存路径
            timestamp: 提取时间戳（秒）
        """
        try:
            cmd = [
                settings.FFMPEG_PATH,
                "-y",
                "-i",
                str(video_path),
                "-ss",
                str(timestamp),
                "-vframes",
                "1",
                "-vf",
                "scale=320:180",
                str(thumbnail_path),
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            await process.communicate()

            if not thumbnail_path.exists():
                logger.warning(f"Thumbnail generation failed for {video_path}")

        except Exception as e:
            logger.error(f"Thumbnail generation error: {e}")

    async def combine_audio_video(
        self, video_path: Path, audio_path: Path, output_path: Path
    ) -> bool:
        """
        合并音频和视频

        Args:
            video_path: 视频文件路径
            audio_path: 音频文件路径
            output_path: 输出文件路径

        Returns:
            是否成功
        """
        if not self.ffmpeg_available:
            logger.warning("FFmpeg not available, cannot combine audio and video")
            return False

        try:
            cmd = [
                settings.FFMPEG_PATH,
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(audio_path),
                "-c:v",
                "copy",
                "-c:a",
                "aac",
                "-shortest",
                str(output_path),
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            await process.communicate()

            return process.returncode == 0

        except Exception as e:
            logger.error(f"Audio-video combination failed: {e}")
            return False

    async def add_watermark(
        self, video_path: Path, watermark_text: str, output_path: Path
    ) -> bool:
        """
        添加水印到视频

        Args:
            video_path: 视频文件路径
            watermark_text: 水印文本
            output_path: 输出文件路径

        Returns:
            是否成功
        """
        if not self.ffmpeg_available:
            logger.warning("FFmpeg not available, cannot add watermark")
            return False

        try:
            cmd = [
                settings.FFMPEG_PATH,
                "-y",
                "-i",
                str(video_path),
                "-vf",
                f"drawtext=text='{watermark_text}':fontsize=24:fontcolor=white@0.5:x=10:y=h-th-10",
                "-c:a",
                "copy",
                str(output_path),
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            await process.communicate()

            return process.returncode == 0

        except Exception as e:
            logger.error(f"Watermark addition failed: {e}")
            return False


# 全局实例
video_composer = VideoComposer()
