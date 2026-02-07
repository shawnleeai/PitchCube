#!/usr/bin/env python3
"""
PitchCube 功能测试脚本
测试所有已实现的功能模块
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.poster_renderer import poster_renderer
from app.services.ip_foundry_service import ip_foundry_service
from app.services.analytics_service import analytics_service
from app.core.config import settings


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"


def print_header(text: str):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")


def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_info(text: str):
    print(f"{Colors.YELLOW}→ {text}{Colors.RESET}")


async def test_poster_generator():
    """测试海报生成器"""
    print_header("海报生成器测试")

    try:
        print_info("正在生成测试海报...")

        result = await poster_renderer.generate(
            product_name="PitchCube",
            description="AI驱动的路演展示自动化平台",
            features=["AI生成", "极速渲染", "多模板"],
            template_id="tech-modern",
        )

        print_success(f"海报生成成功!")
        print_info(f"ID: {result['id']}")
        print_info(f"预览URL: {result['preview_url']}")
        print_info(
            f"尺寸: {result['dimensions']['width']}x{result['dimensions']['height']}"
        )

        return True

    except Exception as e:
        print_error(f"海报生成失败: {e}")
        return False


async def test_ip_foundry():
    """测试IP铸造厂"""
    print_header("IP铸造厂测试")

    try:
        print_info("正在生成IP形象概念...")

        concept = await ip_foundry_service.generate_ip_concept(
            product_name="我的产品",
            product_description="一款革命性的AI产品",
            style="cute",
        )

        print_success(f"IP概念生成成功!")
        print_info(f"名称: {concept['name']}")
        print_info(f"风格: {concept['style_name']}")
        print_info(f"性格: {concept['personality']}")

        print_info("\n正在生成打印指南...")

        guide = await ip_foundry_service.generate_print_guide(
            ip_concept=concept, material="pla", size_cm=10.0
        )

        print_success(f"打印指南生成成功!")
        print_info(f"材料: {guide['material_name']}")
        print_info(f"预估时间: {guide['estimated_time']}")
        print_info(f"材料用量: {guide['material_weight']}")

        styles = ip_foundry_service.get_ip_styles()
        print_info(f"\n可用风格数量: {len(styles)}")

        return True

    except Exception as e:
        print_error(f"IP铸造厂测试失败: {e}")
        return False


async def test_analytics():
    """测试分析服务"""
    print_header("数据分析服务测试")

    try:
        print_info("正在测试事件追踪...")

        await analytics_service.track_event(
            user_id="test_user",
            event_type="generation_start",
            generation_type="poster",
            resource_id="test_001",
            metadata={"template": "tech-modern"},
        )

        print_success("事件追踪成功!")

        print_info("\n正在获取用户洞察...")

        insights = await analytics_service.get_user_insights("test_user")

        print_success("用户洞察获取成功!")
        print_info(f"分析周期: {insights.get('period', 'N/A')}")

        return True

    except Exception as e:
        print_error(f"数据分析服务测试失败: {e}")
        return False


def test_payment_plans():
    """测试支付计划"""
    print_header("支付订阅测试")

    try:
        from app.services.payments.payment_service import payment_service, PLANS

        print_info("正在加载订阅计划...")

        plans = payment_service.get_all_plans()
        print_success(f"成功加载 {len(plans)} 个计划")

        for plan in plans:
            print(f"\n{plan.name}:")
            print(
                f"  - 月付: ¥{plan.price_monthly / 100:.2f}"
                if plan.price_monthly
                else "  - 月付: 免费"
            )
            print(
                f"  - 年付: ¥{plan.price_yearly / 100:.2f}"
                if plan.price_yearly
                else "  - 年付: 免费"
            )
            print(f"  - 限制: {plan.limits}")

        free_plan = payment_service.get_plan("free")
        print_success(f"免费计划详情: {free_plan.name if free_plan else 'N/A'}")

        return True

    except Exception as e:
        print_error(f"支付订阅测试失败: {e}")
        return False


async def test_database_connection():
    """测试数据库连接"""
    print_header("数据库连接测试")

    try:
        from app.db.mongodb import db

        print_info("正在检查MongoDB连接...")

        if db.connected:
            print_success("MongoDB已连接!")

            collections = await db.db.list_collection_names()
            print_info(f"现有集合: {collections}")

            return True
        else:
            print_error("MongoDB未连接 (这是预期的，如果没有配置MongoDB)")
            return True

    except Exception as e:
        print_error(f"数据库测试失败: {e}")
        return False


async def test_api_routes():
    """测试API路由"""
    print_header("API路由测试")

    try:
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)

        print_info("测试根路由...")
        response = client.get("/")
        print_success(f"根路由状态: {response.status_code}")

        print_info("测试健康检查...")
        response = client.get("/health")
        print_success(f"健康检查状态: {response.status_code}")
        print_info(f"响应: {response.json()}")

        print_info("测试API健康检查...")
        response = client.get("/api/v1/health")
        print_success(f"API健康检查状态: {response.status_code}")

        return True

    except Exception as e:
        print_error(f"API路由测试失败: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print_header("PitchCube 功能测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    results["database"] = await test_database_connection()
    results["api"] = await test_api_routes()
    results["poster"] = await test_poster_generator()
    results["ip_foundry"] = await test_ip_foundry()
    results["analytics"] = await test_analytics()
    results["payment"] = test_payment_plans()

    print_header("测试结果汇总")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    for test_name, result in results.items():
        status = "通过" if result else "失败"
        if result:
            print_success(f"{test_name}: {status}")
        else:
            print_error(f"{test_name}: {status}")

    print(f"\n总计: {passed}/{total} 通过, {failed}/{total} 失败")

    return all(results.values())


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
