---
name: disk-usage
description: 分析本地home目录或指定目录的磁盘使用情况，识别大文件，按文件类型统计，提供清理建议。当用户询问磁盘空间、home目录占用、查找大文件、清理建议或磁盘分析时使用此技能。
---

# Disk Usage - 磁盘使用分析

## Overview

此技能提供全面的磁盘使用分析功能，帮助用户了解home目录或指定目录的磁盘占用情况，识别大文件，按文件类型统计，并提供清理建议。

## 快速开始

### 基本用法
当用户询问磁盘使用情况时，你可以：

1. **直接运行分析脚本**：
   ```bash
   # 分析当前用户的home目录
   ./scripts/analyze_home_usage.sh
   
   # 分析指定目录
   ./scripts/analyze_home_usage.sh /path/to/directory
   ```

2. **使用Python脚本获取更详细的分析**：
   ```bash
   python3 scripts/disk_analyzer.py
   ```

### 常见用户请求示例
- "帮我看看home目录占用多少空间"
- "查找home目录中的大文件"
- "分析一下哪个目录占用最多空间"
- "给我一些磁盘清理建议"
- "按文件类型统计一下占用情况"

## 功能特性

### 1. 目录大小分析
- 显示总大小
- 按目录层级显示占用情况
- 识别最大的N个目录

### 2. 文件类型统计
- 按文件扩展名统计数量和大小
- 识别占用最多的文件类型
- 支持自定义显示数量

### 3. 大文件查找
- 查找大于指定大小的文件
- 按大小排序显示
- 支持自定义最小文件大小

### 4. 最近文件分析
- 查找最近修改的文件
- 按时间排序显示
- 支持自定义时间范围

### 5. 清理建议
- 提供针对性的清理建议
- 识别常见的可清理目标
- 给出安全清理指导

## 脚本使用指南

### analyze_home_usage.sh (Shell脚本)
**特点**：快速、轻量、无需Python环境

**选项**：
```bash
-h, --help     显示帮助信息
-s, --summary  只显示摘要
-t, --top N    显示最大的N个目录/文件 (默认: 10)
-d, --depth N  设置扫描深度 (默认: 3)
```

**示例**：
```bash
# 基本分析
./scripts/analyze_home_usage.sh

# 只显示摘要
./scripts/analyze_home_usage.sh -s

# 显示最大的5个目录，深度为2
./scripts/analyze_home_usage.sh -t 5 -d 2

# 分析指定目录
./scripts/analyze_home_usage.sh /var/log
```

### disk_analyzer.py (Python脚本)
**特点**：功能全面、支持JSON输出、可扩展

**选项**：
```bash
-h, --help           显示帮助信息
-s, --summary        只显示摘要
-t TOP, --top TOP    显示最大的N个目录 (默认: 10)
-d DEPTH, --depth DEPTH  扫描深度 (默认: 3)
-m MIN_SIZE, --min-size MIN_SIZE  大文件的最小大小(MB) (默认: 100)
-D DAYS, --days DAYS 最近文件的天数 (默认: 7)
-o OUTPUT, --output OUTPUT  输出到文件
-j, --json           输出JSON格式
```

**示例**：
```bash
# 基本分析
python3 scripts/disk_analyzer.py

# 输出JSON格式
python3 scripts/disk_analyzer.py -j

# 保存到文件
python3 scripts/disk_analyzer.py -o report.txt

# 自定义参数
python3 scripts/disk_analyzer.py -t 20 -d 2 -m 50 -D 30
```

## 使用场景

### 场景1：快速检查磁盘使用
**用户请求**："我的磁盘快满了，帮我看看home目录占用情况"

**响应方式**：
```bash
# 运行快速分析
./scripts/analyze_home_usage.sh -s
```

### 场景2：详细分析大文件
**用户请求**："查找home目录中所有大于100MB的文件"

**响应方式**：
```bash
# 使用Python脚本
python3 scripts/disk_analyzer.py -m 100
```

### 场景3：按文件类型分析
**用户请求**："看看哪种类型的文件占用最多空间"

**响应方式**：
```bash
# 运行完整分析
python3 scripts/disk_analyzer.py
```

### 场景4：定期清理检查
**用户请求**："给我一些磁盘清理建议"

**响应方式**：
1. 运行分析获取当前状态
2. 根据结果提供针对性建议
3. 建议清理临时文件、缓存等

## 最佳实践

### 安全注意事项
1. **权限检查**：确保有读取目标目录的权限
2. **系统目录**：避免分析系统关键目录（如/proc, /sys）
3. **符号链接**：注意处理符号链接，避免重复计算
4. **权限错误**：正确处理权限不足的目录

### 性能优化
1. **深度限制**：合理设置扫描深度，避免过深遍历
2. **结果限制**：限制显示结果数量，避免输出过长
3. **缓存利用**：考虑使用缓存提高重复分析速度

### 用户体验
1. **进度提示**：长时间运行时提供进度反馈
2. **可读格式**：使用人类可读的大小单位
3. **颜色标记**：使用颜色或符号突出重点信息
4. **交互选项**：提供交互式清理选项

## 资源文件

### scripts/
此目录包含可执行的脚本文件：

#### analyze_home_usage.sh
**功能**：快速分析home目录磁盘使用情况的Shell脚本
**特点**：
- 轻量级，无需Python环境
- 快速执行，适合快速检查
- 提供基本分析和清理建议

**主要功能**：
1. 显示总大小和目录摘要
2. 按深度显示最大的目录
3. 按文件类型统计
4. 查找大文件（>100MB）
5. 显示最近修改的文件
6. 提供清理建议

#### disk_analyzer.py
**功能**：功能全面的磁盘分析Python脚本
**特点**：
- 支持JSON输出
- 更多自定义选项
- 更准确的大小计算
- 可扩展的架构

**主要功能**：
1. 详细的目录大小分析
2. 按文件类型统计（支持更多格式）
3. 自定义大文件查找
4. 最近文件分析（可自定义时间范围）
5. JSON格式输出支持
6. 输出到文件功能

### 使用示例

#### 示例1：快速检查
```bash
# 使用Shell脚本快速检查
cd /home/allen/.openclaw/workspace/skills/disk-usage
./scripts/analyze_home_usage.sh
```

#### 示例2：详细分析
```bash
# 使用Python脚本进行详细分析
cd /home/allen/.openclaw/workspace/skills/disk-usage
python3 scripts/disk_analyzer.py -t 20 -d 4 -m 50
```

#### 示例3：生成JSON报告
```bash
# 生成JSON格式的报告
python3 scripts/disk_analyzer.py -j -o disk_report.json
```

## 集成到OpenClaw

### 作为技能使用
当用户询问磁盘相关问题时，此技能会自动触发。你可以：

1. **直接运行脚本**为用户提供分析结果
2. **解释分析结果**并提供清理建议
3. **根据用户需求**调整分析参数

### 常见响应模式
```bash
# 模式1：快速响应
用户："我的磁盘空间不足了"
响应：运行 ./scripts/analyze_home_usage.sh -s 并提供摘要

# 模式2：详细分析
用户："帮我详细分析一下home目录"
响应：运行 python3 scripts/disk_analyzer.py 并提供完整报告

# 模式3：特定查找
用户："查找所有大于500MB的文件"
响应：运行 python3 scripts/disk_analyzer.py -m 500
```

## 维护和更新

### 添加新功能
1. 在 `disk_analyzer.py` 中添加新分析功能
2. 在 `analyze_home_usage.sh` 中添加对应的快速功能
3. 更新SKILL.md文档

### 测试脚本
```bash
# 测试Shell脚本
./scripts/analyze_home_usage.sh --help
./scripts/analyze_home_usage.sh -s

# 测试Python脚本
python3 scripts/disk_analyzer.py --help
python3 scripts/disk_analyzer.py -s
```

### 性能考虑
1. **大目录扫描**：考虑添加进度指示
2. **权限处理**：优雅处理权限错误
3. **输出优化**：控制输出长度，避免过长

---

**技能创建完成！** 现在你可以使用这个技能来帮助用户分析磁盘使用情况了。
