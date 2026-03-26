#!/bin/bash

# analyze_home_usage.sh - 分析home目录磁盘使用情况
# 用法: ./analyze_home_usage.sh [选项] [目录]
# 选项:
#   -h, --help     显示帮助信息
#   -s, --summary  只显示摘要
#   -t, --top N    显示最大的N个目录/文件
#   -d, --depth N  设置扫描深度

set -e

# 默认值
TARGET_DIR="${HOME}"
SHOW_SUMMARY=false
TOP_COUNT=10
MAX_DEPTH=3
SHOW_HELP=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            SHOW_HELP=true
            shift
            ;;
        -s|--summary)
            SHOW_SUMMARY=true
            shift
            ;;
        -t|--top)
            TOP_COUNT="$2"
            shift 2
            ;;
        -d|--depth)
            MAX_DEPTH="$2"
            shift 2
            ;;
        *)
            TARGET_DIR="$1"
            shift
            ;;
    esac
done

# 显示帮助
if [ "$SHOW_HELP" = true ]; then
    echo "用法: $0 [选项] [目录]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -s, --summary  只显示摘要"
    echo "  -t, --top N    显示最大的N个目录/文件 (默认: 10)"
    echo "  -d, --depth N  设置扫描深度 (默认: 3)"
    echo ""
    echo "示例:"
    echo "  $0                    # 分析当前用户的home目录"
    echo "  $0 /path/to/dir       # 分析指定目录"
    echo "  $0 -t 5 -d 2          # 显示最大的5个目录，深度为2"
    echo "  $0 -s                 # 只显示摘要"
    exit 0
fi

# 检查目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "错误: 目录 '$TARGET_DIR' 不存在"
    exit 1
fi

echo "=========================================="
echo "磁盘使用分析: $TARGET_DIR"
echo "=========================================="
echo ""

# 获取总大小
TOTAL_SIZE=$(du -sh "$TARGET_DIR" 2>/dev/null | cut -f1)
echo "📊 总大小: $TOTAL_SIZE"
echo ""

if [ "$SHOW_SUMMARY" = true ]; then
    echo "📁 目录结构摘要:"
    du -h --max-depth=1 "$TARGET_DIR" 2>/dev/null | sort -hr | head -20
    exit 0
fi

echo "📈 最大的 $TOP_COUNT 个目录 (深度 $MAX_DEPTH):"
echo ""

# 显示最大的目录
find "$TARGET_DIR" -maxdepth "$MAX_DEPTH" -type d -exec du -sh {} \; 2>/dev/null | \
    sort -hr | \
    head -n "$TOP_COUNT" | \
    while read size path; do
        printf "%-10s %s\n" "$size" "$path"
    done

echo ""
echo "📋 按文件类型统计:"
echo ""

# 按文件类型统计
echo "文件类型统计 (前10种):"
find "$TARGET_DIR" -type f 2>/dev/null | \
    awk -F. '{if (NF>1) print $NF}' | \
    sort | uniq -c | sort -rn | head -10 | \
    while read count ext; do
        printf "  %-10s %s\n" "$count" "$ext"
    done

echo ""
echo "🗑️ 可能的大文件 (大于100MB):"
echo ""

# 查找大文件
find "$TARGET_DIR" -type f -size +100M 2>/dev/null | \
    xargs -I {} du -h {} 2>/dev/null | \
    sort -hr | head -10 | \
    while read size path; do
        printf "  %-10s %s\n" "$size" "$path"
    done

echo ""
echo "📅 最近修改的文件 (7天内):"
echo ""

# 最近修改的文件
find "$TARGET_DIR" -type f -mtime -7 2>/dev/null | \
    xargs -I {} du -h {} 2>/dev/null | \
    sort -hr | head -5 | \
    while read size path; do
        printf "  %-10s %s\n" "$size" "$path"
    done

echo ""
echo "=========================================="
echo "💡 清理建议:"
echo "1. 检查大文件是否还需要"
echo "2. 清理临时文件 (~/.cache, ~/.local/share/Trash)"
echo "3. 删除旧的下载文件 (~/Downloads)"
echo "4. 清理Docker镜像 (如果使用Docker)"
echo "=========================================="