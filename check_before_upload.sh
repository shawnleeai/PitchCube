#!/bin/bash
# PitchCube GitHub 上传前最终检查脚本
# 运行此脚本确保项目已准备好上传到 GitHub

echo "=========================================="
echo "  PitchCube GitHub 上传前检查"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查标记
ERRORS=0
WARNINGS=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# 1. 检查泄露的 API 密钥
echo "1. 检查敏感信息泄露..."
if grep -r "2qksj2la6ilZLiLnyIWRGSQdYpOjy0p6gdnWBUXut6P33xF6Vlo0b388bv3OYBKcL" . --include="*.py" --include="*.md" --include="*.env" 2>/dev/null | grep -v ".git"; then
    check_fail "发现泄露的 API 密钥！"
else
    check_pass "未泄露 API 密钥"
fi

# 2. 检查真实 .env 文件
echo ""
echo "2. 检查 .env 文件..."
ENV_COUNT=$(find . -name ".env" -type f | grep -v ".example" | grep -v ".git" | wc -l)
if [ $ENV_COUNT -eq 0 ]; then
    check_pass "无真实的 .env 文件 ($ENV_COUNT 个)"
else
    check_fail "发现 $ENV_COUNT 个真实的 .env 文件"
    find . -name ".env" -type f | grep -v ".example" | grep -v ".git"
fi

# 3. 检查必要文件
echo ""
echo "3. 检查必要文件..."

FILES=("README.md" "LICENSE" "CONTRIBUTING.md" "CODE_OF_CONDUCT.md" "SECURITY.md")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file 存在"
    else
        check_fail "$file 缺失"
    fi
done

# 4. 检查 GitHub 配置
echo ""
echo "4. 检查 GitHub 配置..."

if [ -d ".github" ]; then
    check_pass ".github 目录存在"
    
    if [ -d ".github/ISSUE_TEMPLATE" ]; then
        check_pass "Issue 模板已配置"
    else
        check_fail "Issue 模板缺失"
    fi
    
    if [ -d ".github/workflows" ]; then
        check_pass "CI/CD 工作流已配置"
        WORKFLOW_COUNT=$(ls .github/workflows/*.yml 2>/dev/null | wc -l)
        echo "   发现 $WORKFLOW_COUNT 个工作流文件"
    else
        check_fail "CI/CD 工作流缺失"
    fi
else
    check_fail ".github 目录缺失"
fi

# 5. 检查 .gitignore
echo ""
echo "5. 检查 .gitignore..."

if [ -f ".gitignore" ]; then
    check_pass ".gitignore 存在"
    
    # 检查关键忽略项
    if grep -q "node_modules" .gitignore; then
        check_pass "node_modules 已配置忽略"
    else
        check_warn "node_modules 未配置忽略"
    fi
    
    if grep -q ".next" .gitignore; then
        check_pass ".next 已配置忽略"
    else
        check_warn ".next 未配置忽略"
    fi
    
    if grep -q ".env" .gitignore; then
        check_pass ".env 已配置忽略"
    else
        check_fail ".env 未配置忽略"
    fi
else
    check_fail ".gitignore 缺失"
fi

# 6. 检查项目结构
echo ""
echo "6. 检查项目结构..."

if [ -d "backend" ]; then
    check_pass "backend 目录存在"
    if [ -f "backend/requirements.txt" ]; then
        check_pass "backend/requirements.txt 存在"
    else
        check_fail "backend/requirements.txt 缺失"
    fi
else
    check_fail "backend 目录缺失"
fi

if [ -d "frontend" ]; then
    check_pass "frontend 目录存在"
    if [ -f "frontend/package.json" ]; then
        check_pass "frontend/package.json 存在"
    else
        check_fail "frontend/package.json 缺失"
    fi
else
    check_fail "frontend 目录缺失"
fi

# 7. 检查重复文件
echo ""
echo "7. 检查重复/旧文件..."

OLD_FILES=$(find . -type f \( -name "*enhanced*" -o -name "*old*" -o -name "*backup*" -o -name "*copy*" \) 2>/dev/null | grep -v node_modules | grep -v __pycache__ | grep -v .next | grep -v .git | wc -l)

if [ $OLD_FILES -eq 0 ]; then
    check_pass "无残留的旧文件"
else
    check_warn "发现 $OLD_FILES 个可能残留的文件"
    find . -type f \( -name "*enhanced*" -o -name "*old*" -o -name "*backup*" \) 2>/dev/null | grep -v node_modules | grep -v __pycache__ | grep -v .next | grep -v .git | head -5
fi

# 8. 检查大文件
echo ""
echo "8. 检查大文件 (>5MB)..."

LARGE_FILES=$(find . -type f -size +5M 2>/dev/null | grep -v node_modules | grep -v __pycache__ | grep -v .next | grep -v .git | wc -l)

if [ $LARGE_FILES -eq 0 ]; then
    check_pass "无大文件"
else
    check_warn "发现 $LARGE_FILES 个大文件 (检查是否在 .gitignore 中)"
    find . -type f -size +5M 2>/dev/null | grep -v node_modules | grep -v __pycache__ | grep -v .next | grep -v .git | head -3
fi

# 9. 统计文件数
echo ""
echo "9. 项目统计..."

FILE_COUNT=$(find . -type f | grep -v node_modules | grep -v __pycache__ | grep -v .next | grep -v .git | wc -l)
echo "   总文件数: $FILE_COUNT"

echo ""
echo "=========================================="

# 最终结果
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ 检查通过！项目已准备好上传到 GitHub${NC}"
    echo ""
    echo "建议操作:"
    echo "  1. 确保已在 StepFun 平台撤销旧 API 密钥"
    echo "  2. 运行: git init && git add . && git commit -m 'Initial commit'"
    echo "  3. 推送到 GitHub: git push -u origin main"
    
    if [ $WARNINGS -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠️  有 $WARNINGS 个警告，建议查看但不影响上传${NC}"
    fi
else
    echo -e "${RED}❌ 检查未通过！发现 $ERRORS 个错误${NC}"
    echo ""
    echo "请先修复上述错误，然后再上传到 GitHub"
    exit 1
fi

echo "=========================================="
