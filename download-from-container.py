#!/usr/bin/env python3
"""
从远程容器下载所有文件到本地

功能：
1. 连接到远程服务器
2. 从容器内导出所有文件到服务器临时目录
3. 通过SFTP下载文件到本地
4. 清理服务器临时文件

使用方法：
    python download-from-container.py

配置：
    - 需要 password.txt 文件包含 SSH 连接信息
    - 格式：<IP> <用户名> <密码>
    - 例子：192.168.1.100 root mypassword

下载位置：
    e:\\Qoder_workspace\\xianyu-auto-reply\\container_backup

排除规则：
    - node_modules (前端依赖太大)
    - __pycache__, *.pyc (编译缓存)
    - SQLite 临时文件
"""

# 版本：v1.0
# 创建时间：2025-12-20

import paramiko
import os
import sys
from pathlib import Path
import time

# 读取密码文件
with open(r'e:\Qoder_workspace\xianyu-auto-reply\password.txt', 'r') as f:
    line = f.readline().strip()
    ip, user, password = line.split()

# 本地保存路径
local_base = r'e:\Qoder_workspace\xianyu-auto-reply\container_backup'

# 容器内路径
container_name = 'xianyu-auto-reply'
container_path = '/app'

# 远程临时目录（用于存储从容器导出的文件）
remote_temp_base = '/tmp/container_export_' + str(int(time.time()))

# 需要排除的文件/目录
exclude_patterns = [
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '*.pyc',
    '*.pyo',
    '.DS_Store',
    'Thumbs.db',
    'node_modules',  # 前端依赖太大
    'data/xianyu.db-wal',  # SQLite临时文件
    'data/xianyu.db-shm',
]

def should_exclude(path):
    """检查路径是否应该被排除"""
    path_str = str(path)
    for pattern in exclude_patterns:
        if '*' in pattern:
            # 简单的通配符匹配
            pattern_cleaned = pattern.replace('*', '')
            if path_str.endswith(pattern_cleaned):
                return True
        elif pattern in path_str:
            return True
    return False

print("=" * 60)
print("容器文件下载工具")
print("=" * 60)
print(f"容器名称: {container_name}")
print(f"容器路径: {container_path}")
print(f"本地保存: {local_base}")
print("=" * 60)

# 创建本地保存目录
Path(local_base).mkdir(parents=True, exist_ok=True)

# 创建SSH连接
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"\n[1/5] 连接到远程服务器 {ip}...")
    ssh.connect(ip, username=user, password=password, timeout=10)
    print("✅ 连接成功")
    
    # 检查容器是否运行
    print(f"\n[2/5] 检查容器状态...")
    stdin, stdout, stderr = ssh.exec_command(f"docker ps --filter name={container_name} --format '{{{{.Names}}}}'")
    container_running = stdout.read().decode('utf-8').strip()
    
    if container_running != container_name:
        print(f"❌ 容器 {container_name} 未运行")
        sys.exit(1)
    print(f"✅ 容器运行中")
    
    # 创建远程临时目录
    print(f"\n[3/5] 准备临时目录...")
    ssh.exec_command(f"mkdir -p {remote_temp_base}")
    print(f"✅ 临时目录: {remote_temp_base}")
    
    # 从容器复制文件到服务器
    print(f"\n[4/5] 从容器导出文件...")
    cmd = f"docker cp {container_name}:{container_path}/. {remote_temp_base}/"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    
    if exit_code != 0:
        err = stderr.read().decode('utf-8')
        print(f"❌ 导出失败: {err}")
        sys.exit(1)
    print(f"✅ 文件已导出到服务器临时目录")
    
    # 获取所有文件列表
    print(f"\n[5/5] 下载文件到本地...")
    cmd = f"find {remote_temp_base} -type f"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    file_list = stdout.read().decode('utf-8').strip().split('\n')
    
    # 创建SFTP客户端
    sftp = ssh.open_sftp()
    
    downloaded_count = 0
    failed_count = 0
    skipped_count = 0
    total_files = len(file_list)
    
    print(f"找到 {total_files} 个文件")
    print("-" * 60)
    
    for remote_file in file_list:
        if not remote_file.strip():
            continue
            
        # 计算相对路径
        rel_path = remote_file.replace(remote_temp_base + '/', '')
        
        # 检查是否需要排除
        if should_exclude(rel_path):
            skipped_count += 1
            continue
        
        # 计算本地路径
        local_file = os.path.join(local_base, rel_path.replace('/', os.sep))
        local_dir = os.path.dirname(local_file)
        
        try:
            # 创建本地目录
            Path(local_dir).mkdir(parents=True, exist_ok=True)
            
            # 下载文件
            sftp.get(remote_file, local_file)
            downloaded_count += 1
            
            # 显示进度
            if downloaded_count % 10 == 0 or downloaded_count == total_files:
                print(f"进度: {downloaded_count}/{total_files - skipped_count} | 最新: {rel_path[:60]}")
            
        except Exception as e:
            failed_count += 1
            print(f"❌ 下载失败: {rel_path} - {e}")
    
    sftp.close()
    
    # 清理远程临时目录
    print(f"\n清理远程临时文件...")
    ssh.exec_command(f"rm -rf {remote_temp_base}")
    
    print("\n" + "=" * 60)
    print("下载完成！")
    print("=" * 60)
    print(f"✅ 成功下载: {downloaded_count} 个文件")
    print(f"⏭️  已跳过: {skipped_count} 个文件（排除规则）")
    print(f"❌ 下载失败: {failed_count} 个文件")
    print(f"📁 保存位置: {local_base}")
    print("=" * 60)
    
except KeyboardInterrupt:
    print("\n\n操作已取消")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ 错误: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    ssh.close()
