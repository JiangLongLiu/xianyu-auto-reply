import paramiko
import sys
import os

# 读取密码文件
with open(r'e:\Qoder_workspace\xianyu-auto-reply\password.txt', 'r') as f:
    line = f.readline().strip()
    ip, user, password = line.split()

# 创建 SSH 客户端
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # 连接到远程服务器
    ssh.connect(ip, username=user, password=password, timeout=10)
    
    # 创建 SFTP 客户端
    sftp = ssh.open_sftp()
    
    # 获取本地文件和远程路径
    if len(sys.argv) != 3:
        print("用法: python ssh-upload.py <本地文件> <远程路径>")
        sys.exit(1)
    
    local_file = sys.argv[1]
    remote_path = sys.argv[2]
    
    if not os.path.exists(local_file):
        print(f"错误: 本地文件不存在: {local_file}")
        sys.exit(1)
    
    print(f"正在上传: {local_file} -> {remote_path}")
    sftp.put(local_file, remote_path)
    print("上传成功！")
    
    sftp.close()
    
except Exception as e:
    print(f"错误: {e}", file=sys.stderr)
    sys.exit(1)
finally:
    ssh.close()
