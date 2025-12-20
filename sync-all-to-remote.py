import paramiko
import os
import sys
from pathlib import Path

# 读取密码文件
with open(r'e:\Qoder_workspace\xianyu-auto-reply\password.txt', 'r') as f:
    line = f.readline().strip()
    ip, user, password = line.split()

# 本地项目路径
local_base = r'e:\Qoder_workspace\xianyu-auto-reply'

# 远程目录
remote_base = '/mnt/sata1-1/docker/mycontainers/xianyu-auto-reply'

# 需要排除的文件/目录（避免上传不必要的文件）
exclude_patterns = [
    '__pycache__',
    '.git',
    'node_modules',
    '.pytest_cache',
    '.mypy_cache',
    '*.pyc',
    '*.pyo',
    '.DS_Store',
    'Thumbs.db',
    'password.txt',  # 敏感文件
    'XianyuAutoAsync_fixed.py',  # 临时文件
    'download-fixed-file.py',  # 临时脚本
]

def should_exclude(path):
    """检查路径是否应该被排除"""
    path_str = str(path)
    for pattern in exclude_patterns:
        if pattern in path_str:
            return True
    return False

def get_all_files(base_path):
    """递归获取所有文件（包括git忽略的）"""
    files = []
    base = Path(base_path)
    
    for item in base.rglob('*'):
        if item.is_file() and not should_exclude(item):
            rel_path = item.relative_to(base)
            files.append((str(item), str(rel_path)))
    
    return files

print("正在扫描本地文件...")
all_files = get_all_files(local_base)
print(f"找到 {len(all_files)} 个文件需要上传")

# 创建SSH连接
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print(f"\n连接到 {ip}...")
    ssh.connect(ip, username=user, password=password, timeout=10)
    
    # 创建SFTP客户端
    sftp = ssh.open_sftp()
    
    uploaded_count = 0
    failed_count = 0
    
    for local_path, rel_path in all_files:
        remote_path = f"{remote_base}/{rel_path.replace(chr(92), '/')}"  # 替换Windows路径分隔符
        remote_dir = os.path.dirname(remote_path)
        
        try:
            # 确保远程目录存在
            try:
                sftp.stat(remote_dir)
            except FileNotFoundError:
                # 递归创建目录
                dirs = []
                temp_dir = remote_dir
                while temp_dir != remote_base:
                    dirs.insert(0, temp_dir)
                    temp_dir = os.path.dirname(temp_dir)
                
                for d in dirs:
                    try:
                        sftp.stat(d)
                    except FileNotFoundError:
                        sftp.mkdir(d)
            
            # 上传文件
            sftp.put(local_path, remote_path)
            uploaded_count += 1
            print(f"✅ [{uploaded_count}/{len(all_files)}] {rel_path}")
            
        except Exception as e:
            failed_count += 1
            print(f"❌ 失败: {rel_path} - {e}")
    
    sftp.close()
    
    print(f"\n上传完成！")
    print(f"成功: {uploaded_count} 个文件")
    print(f"失败: {failed_count} 个文件")
    
    # 同步到容器
    if uploaded_count > 0:
        print(f"\n正在同步文件到容器...")
        
        # 获取需要同步到容器的文件列表
        important_files = [
            'XianyuAutoAsync.py',
            'Start.py',
            'reply_server.py',
            'config.py',
            'db_manager.py',
            'entrypoint.sh',
        ]
        
        for filename in important_files:
            cmd = f"docker cp {remote_base}/{filename} xianyu-auto-reply:/app/{filename} 2>/dev/null"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            exit_code = stdout.channel.recv_exit_status()
            if exit_code == 0:
                print(f"  ✅ {filename} 已同步到容器")
            else:
                err = stderr.read().decode('utf-8')
                if err and 'No such file' not in err:
                    print(f"  ⚠️ {filename} 同步失败: {err.strip()}")
        
        print("\n是否需要重启容器使所有更改生效？")
        print("运行以下命令重启容器：")
        print(f"python ssh-exec.py \"cd {remote_base} && /usr/local/bin/docker-compose -f docker-compose-mybuild.yml restart\"")
    
except Exception as e:
    print(f"错误: {e}", file=sys.stderr)
    sys.exit(1)
finally:
    ssh.close()
