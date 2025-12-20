import paramiko
import time
import re
from datetime import datetime

# 读取密码文件
with open(r'e:\Qoder_workspace\xianyu-auto-reply\password.txt', 'r') as f:
    line = f.readline().strip()
    ip, user, password = line.split()

def get_build_status():
    """获取构建状态"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(ip, username=user, password=password, timeout=10)
        
        # 获取日志最后30行
        cmd = "tail -30 /mnt/sata1-1/docker/mycontainers/xianyu-auto-reply/build-final.log"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        log_output = stdout.read().decode('utf-8')
        
        # 检查是否完成
        if 'Successfully built' in log_output and 'Successfully tagged' in log_output:
            return 'completed', log_output
        
        # 检查是否失败
        if 'Error' in log_output or 'failed' in log_output:
            # 获取最后100行以显示错误详情
            cmd = "tail -100 /mnt/sata1-1/docker/mycontainers/xianyu-auto-reply/build-final.log"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            error_log = stdout.read().decode('utf-8')
            return 'failed', error_log
        
        # 提取当前步骤
        step_match = re.search(r'Step (\d+)/(\d+)', log_output)
        if step_match:
            current = step_match.group(1)
            total = step_match.group(2)
            return 'building', f"Step {current}/{total}"
        
        return 'building', 'Initializing...'
        
    except Exception as e:
        return 'error', str(e)
    finally:
        ssh.close()

print("🔄 开始监控Docker镜像构建...")
print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 60)

start_time = time.time()
last_status = None
check_count = 0

while True:
    check_count += 1
    elapsed = int(time.time() - start_time)
    elapsed_min = elapsed // 60
    elapsed_sec = elapsed % 60
    
    status, info = get_build_status()
    
    if status != last_status or check_count % 5 == 0:  # 每5次检查输出一次或状态变化时输出
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] 已用时: {elapsed_min}分{elapsed_sec}秒 | 状态: {info}")
        last_status = status
    
    if status == 'completed':
        print("\n" + "=" * 60)
        print("✅ 构建成功完成！")
        print(f"⏰ 总耗时: {elapsed_min}分{elapsed_sec}秒")
        print("=" * 60)
        print("\n最后30行日志：")
        print(info)
        break
    
    elif status == 'failed':
        print("\n" + "=" * 60)
        print("❌ 构建失败！")
        print("=" * 60)
        print("\n错误日志（最后100行）：")
        print(info)
        break
    
    elif status == 'error':
        print(f"\n⚠️ 监控错误: {info}")
        print("60秒后重试...")
        time.sleep(60)
        continue
    
    # 每30秒检查一次
    time.sleep(30)
    
    # 超时保护：2小时
    if elapsed > 7200:
        print("\n⚠️ 构建超时（超过2小时），请手动检查")
        break

print("\n监控结束。")
