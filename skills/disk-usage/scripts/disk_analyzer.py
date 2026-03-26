#!/usr/bin/env python3
"""
disk_analyzer.py - 磁盘使用分析工具

功能:
1. 分析指定目录的磁盘使用情况
2. 按文件类型统计
3. 查找大文件
4. 生成可视化报告
5. 提供清理建议
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime, timedelta

def get_human_readable_size(size_bytes):
    """将字节数转换为人类可读的格式"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_directory_size(path):
    """获取目录大小（使用du命令更准确）"""
    try:
        result = subprocess.run(
            ['du', '-sb', path],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            size = int(result.stdout.split()[0])
            return size
    except Exception as e:
        pass
    
    # 如果du失败，使用Python递归计算
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    except (PermissionError, OSError):
        pass
    return total

def analyze_by_file_type(directory, max_types=10):
    """按文件类型统计"""
    type_stats = defaultdict(int)
    type_count = defaultdict(int)
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    # 获取文件扩展名
                    ext = os.path.splitext(file)[1].lower()
                    if not ext:
                        ext = "无扩展名"
                    
                    # 获取文件大小
                    size = os.path.getsize(filepath)
                    type_stats[ext] += size
                    type_count[ext] += 1
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    
    # 按大小排序
    sorted_types = sorted(type_stats.items(), key=lambda x: x[1], reverse=True)
    
    return sorted_types[:max_types], type_count

def find_large_files(directory, min_size_mb=100, max_results=20):
    """查找大文件"""
    large_files = []
    min_size_bytes = min_size_mb * 1024 * 1024
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    size = os.path.getsize(filepath)
                    if size >= min_size_bytes:
                        large_files.append((filepath, size))
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    
    # 按大小排序
    large_files.sort(key=lambda x: x[1], reverse=True)
    return large_files[:max_results]

def find_recent_files(directory, days=7, max_results=20):
    """查找最近修改的文件"""
    recent_files = []
    cutoff_time = datetime.now() - timedelta(days=days)
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if mtime > cutoff_time:
                        size = os.path.getsize(filepath)
                        recent_files.append((filepath, size, mtime))
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    
    # 按修改时间排序
    recent_files.sort(key=lambda x: x[2], reverse=True)
    return recent_files[:max_results]

def get_top_directories(directory, max_depth=3, top_n=10):
    """获取最大的目录"""
    try:
        # 使用du命令获取目录大小
        cmd = ['du', '-h', '--max-depth', str(max_depth), directory]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # 解析并排序
            dir_sizes = []
            for line in lines:
                if line:
                    parts = line.split('\t')
                    if len(parts) == 2:
                        size, path = parts
                        dir_sizes.append((size, path))
            
            # 按大小排序（需要解析人类可读的大小）
            def parse_size(size_str):
                """将人类可读大小转换为字节数用于排序"""
                units = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
                if size_str[-1] in units:
                    num = float(size_str[:-1])
                    unit = size_str[-1]
                    return num * units[unit]
                return float(size_str)
            
            dir_sizes.sort(key=lambda x: parse_size(x[0]), reverse=True)
            return dir_sizes[:top_n]
    except Exception as e:
        pass
    
    return []

def generate_report(directory, options):
    """生成分析报告"""
    report = []
    
    report.append("=" * 60)
    report.append(f"磁盘使用分析报告: {directory}")
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    report.append("")
    
    # 总大小
    total_size = get_directory_size(directory)
    report.append(f"📊 总大小: {get_human_readable_size(total_size)}")
    report.append("")
    
    if options.summary:
        # 显示摘要
        report.append("📁 目录结构摘要:")
        top_dirs = get_top_directories(directory, max_depth=1, top_n=20)
        for size, path in top_dirs:
            report.append(f"  {size:>10}  {path}")
        return "\n".join(report)
    
    # 最大的目录
    report.append(f"📈 最大的 {options.top} 个目录 (深度 {options.depth}):")
    top_dirs = get_top_directories(directory, max_depth=options.depth, top_n=options.top)
    for size, path in top_dirs:
        report.append(f"  {size:>10}  {path}")
    report.append("")
    
    # 按文件类型统计
    report.append("📋 按文件类型统计:")
    file_types, type_count = analyze_by_file_type(directory, max_types=10)
    for ext, size in file_types:
        count = type_count.get(ext, 0)
        report.append(f"  {ext:>15}: {count:>6} 个文件, {get_human_readable_size(size):>10}")
    report.append("")
    
    # 大文件
    report.append(f"🗑️ 可能的大文件 (大于 {options.min_size}MB):")
    large_files = find_large_files(directory, min_size_mb=options.min_size, max_results=10)
    for path, size in large_files:
        report.append(f"  {get_human_readable_size(size):>10}  {path}")
    report.append("")
    
    # 最近修改的文件
    report.append(f"📅 最近修改的文件 ({options.days}天内):")
    recent_files = find_recent_files(directory, days=options.days, max_results=5)
    for path, size, mtime in recent_files:
        report.append(f"  {get_human_readable_size(size):>10}  {mtime.strftime('%Y-%m-%d')}  {path}")
    report.append("")
    
    # 清理建议
    report.append("=" * 60)
    report.append("💡 清理建议:")
    report.append("1. 检查大文件是否还需要")
    report.append("2. 清理临时文件 (~/.cache, ~/.local/share/Trash)")
    report.append("3. 删除旧的下载文件 (~/Downloads)")
    report.append("4. 清理Docker镜像 (如果使用Docker)")
    report.append("5. 清理旧的日志文件 (/var/log, ~/.npm/_logs)")
    report.append("6. 检查重复文件")
    report.append("7. 清理浏览器缓存")
    report.append("=" * 60)
    
    return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description='磁盘使用分析工具')
    parser.add_argument('directory', nargs='?', default=os.path.expanduser('~'),
                       help='要分析的目录 (默认: 用户home目录)')
    parser.add_argument('-s', '--summary', action='store_true',
                       help='只显示摘要')
    parser.add_argument('-t', '--top', type=int, default=10,
                       help='显示最大的N个目录 (默认: 10)')
    parser.add_argument('-d', '--depth', type=int, default=3,
                       help='扫描深度 (默认: 3)')
    parser.add_argument('-m', '--min-size', type=int, default=100,
                       help='大文件的最小大小(MB) (默认: 100)')
    parser.add_argument('-D', '--days', type=int, default=7,
                       help='最近文件的天数 (默认: 7)')
    parser.add_argument('-o', '--output', 
                       help='输出到文件')
    parser.add_argument('-j', '--json', action='store_true',
                       help='输出JSON格式')
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.exists(args.directory):
        print(f"错误: 目录 '{args.directory}' 不存在")
        sys.exit(1)
    
    if not os.path.isdir(args.directory):
        print(f"错误: '{args.directory}' 不是目录")
        sys.exit(1)
    
    if args.json:
        # JSON输出
        data = {
            "directory": args.directory,
            "timestamp": datetime.now().isoformat(),
            "total_size": get_directory_size(args.directory),
            "top_directories": get_top_directories(args.directory, args.depth, args.top),
            "large_files": [(path, size) for path, size in find_large_files(args.directory, args.min_size, 10)],
            "recent_files": [(path, size, mtime.isoformat()) for path, size, mtime in find_recent_files(args.directory, args.days, 5)]
        }
        
        output = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        # 文本输出
        output = generate_report(args.directory, args)
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"报告已保存到: {args.output}")
    else:
        print(output)

if __name__ == '__main__':
    main()