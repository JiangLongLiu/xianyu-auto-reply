#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动监控构建进度，构建完成后自动部署和验证
"""
import subprocess
import time
import sys
import re

def run_ssh_command(command):
    """执行SSH命令"""
    try:
        result = subprocess.run(
            ["python", "ssh-exec.py", command],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout
    except Exception as e:
        print(f"执行命令失败: {e}")
        return ""

def check_build_status():
    """检查构建状态"""
    output = run_ssh_command("tail -50 /mnt/sata1-1/docker/mycontainers/xianyu-auto-reply/build2.log")
    
    # 检查是否构建完成
    if "Successfully built" in output or "Successfully tagged" in output:
        return "completed"
    
    # 检查是否有错误
    if "ERROR" in output or "Error" in output:
        return "error"
    
    # 检查当前步骤
    step_match = re.search(r'Step (\d+)/(\d+)', output)
    if step_match:
        current = step_match.group(1)
        total = step_match.group(2)
        return f"building_{current}/{total}"
    
    return "building"

def deploy_container():
    """部署容器"""
    print("\n" + "="*60)
    print("🚀 开始部署新容器...")
    print("="*60)
    
    # 停止旧容器
    print("\n1️⃣ 停止旧容器...")
    output = run_ssh_command(
        "cd /mnt/sata1-1/docker/mycontainers/xianyu-auto-reply && "
        "/usr/local/bin/docker-compose -f docker-compose-mybuild.yml down"
    )
    print(output)
    
    # 启动新容器
    print("\n2️⃣ 启动新容器...")
    output = run_ssh_command(
        "cd /mnt/sata1-1/docker/mycontainers/xianyu-auto-reply && "
        "/usr/local/bin/docker-compose -f docker-compose-mybuild.yml up -d"
    )
    print(output)
    
    # 等待容器启动
    print("\n⏳ 等待容器启动（10秒）...")
    time.sleep(10)
    
    # 检查容器状态
    print("\n3️⃣ 检查容器状态...")
    output = run_ssh_command("docker ps | grep xianyu")
    print(output)
    
    if "xianyu-auto-reply" in output and "Up" in output:
        print("✅ 容器启动成功！")
        return True
    else:
        print("❌ 容器启动失败！")
        return False

def verify_xvfb():
    """验证Xvfb配置"""
    print("\n" + "="*60)
    print("🔍 开始验证Xvfb配置...")
    print("="*60)
    
    # 等待容器完全启动
    print("\n⏳ 等待容器完全启动（20秒）...")
    time.sleep(20)
    
    # 检查Xvfb进程
    print("\n1️⃣ 检查Xvfb进程...")
    output = run_ssh_command("docker exec xianyu-auto-reply ps | grep Xvfb")
    if "Xvfb" in output:
        print(f"✅ Xvfb进程运行中:\n{output}")
    else:
        print("❌ Xvfb进程未运行")
        print(f"输出: {output}")
    
    # 检查DISPLAY环境变量
    print("\n2️⃣ 检查DISPLAY环境变量...")
    output = run_ssh_command("docker exec xianyu-auto-reply sh -c 'echo $DISPLAY'")
    if ":99" in output:
        print(f"✅ DISPLAY环境变量已设置: {output.strip()}")
    else:
        print(f"❌ DISPLAY环境变量未设置或不正确: {output}")
    
    # 检查启动日志中的Xvfb信息
    print("\n3️⃣ 检查容器启动日志...")
    output = run_ssh_command("docker logs xianyu-auto-reply 2>&1 | grep -E '(Xvfb|DISPLAY)' | head -20")
    if output.strip():
        print(f"📋 Xvfb相关日志:\n{output}")
    else:
        print("⚠️ 未找到Xvfb相关日志")
    
    # 检查entrypoint.sh内容
    print("\n4️⃣ 验证entrypoint.sh是否包含Xvfb代码...")
    output = run_ssh_command("docker exec xianyu-auto-reply grep -A 5 'Xvfb虚拟显示' /app/entrypoint.sh")
    if "Xvfb虚拟显示" in output:
        print("✅ entrypoint.sh包含Xvfb启动代码")
    else:
        print("❌ entrypoint.sh不包含Xvfb启动代码")
    
    # 检查Xvfb是否已安装
    print("\n5️⃣ 检查Xvfb是否已安装...")
    output = run_ssh_command("docker exec xianyu-auto-reply which Xvfb")
    if "/usr/bin/Xvfb" in output:
        print(f"✅ Xvfb已安装: {output.strip()}")
    else:
        print(f"❌ Xvfb未安装: {output}")
    
    print("\n" + "="*60)
    print("✅ 验证完成！")
    print("="*60)

def main():
    """主函数"""
    print("="*60)
    print("🔄 自动构建监控与部署脚本")
    print("="*60)
    
    check_interval = 120  # 每2分钟检查一次
    max_wait_time = 3600 * 2  # 最多等待2小时
    elapsed_time = 0
    
    print(f"\n⏰ 检查间隔: {check_interval}秒")
    print(f"⏰ 最大等待时间: {max_wait_time}秒 ({max_wait_time/60}分钟)")
    
    while elapsed_time < max_wait_time:
        status = check_build_status()
        
        if status == "completed":
            print("\n" + "="*60)
            print("🎉 构建完成！开始部署...")
            print("="*60)
            
            # 部署容器
            if deploy_container():
                # 验证Xvfb
                verify_xvfb()
                print("\n✅ 所有步骤完成！")
                return 0
            else:
                print("\n❌ 部署失败！")
                return 1
        
        elif status == "error":
            print("\n❌ 构建过程中发生错误！")
            print("\n📋 最后50行日志：")
            output = run_ssh_command("tail -50 /mnt/sata1-1/docker/mycontainers/xianyu-auto-reply/build2.log")
            print(output)
            return 1
        
        elif status.startswith("building"):
            print(f"\r⏳ 构建进行中... [{status}] (已等待 {elapsed_time//60} 分钟)", end="", flush=True)
        else:
            print(f"\r⏳ 等待构建开始... (已等待 {elapsed_time//60} 分钟)", end="", flush=True)
        
        time.sleep(check_interval)
        elapsed_time += check_interval
    
    print(f"\n⏰ 超时：等待时间超过 {max_wait_time//60} 分钟")
    return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
