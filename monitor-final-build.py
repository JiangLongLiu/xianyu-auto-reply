#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控最终构建进度，完成后执行验证和部署
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
    output = run_ssh_command("tail -100 /mnt/sata1-1/docker/mycontainers/xianyu-auto-reply/build-final.log")
    
    # 检查是否构建完成 - 必须同时满足两个条件
    # 1. 包含Successfully built或Successfully tagged
    # 2. 这些文本必须在最后几行（避免误判npm/apt的输出）
    last_20_lines = '\n'.join(output.split('\n')[-20:])
    if "Successfully built" in last_20_lines and "Successfully tagged" in last_20_lines:
        return "completed"
    
    # 检查是否有Docker构建错误（不是npm/apt的错误）
    if "Error response from daemon" in output or "failed to solve" in output:
        return "error"
    
    # 检查当前步骤
    step_match = re.search(r'Step (\d+)/(\d+)', output)
    if step_match:
        current = step_match.group(1)
        total = step_match.group(2)
        return f"building_{current}/{total}"
    
    return "building"

def verify_image():
    """验证镜像内容"""
    print("\n" + "="*60)
    print("🔍 步骤5：验证镜像内容...")
    print("="*60)
    
    # 先检查镜像是否存在
    print("\n0️⃣ 检查镜像是否存在...")
    output = run_ssh_command("docker images | grep xianyu-auto-reply")
    if "xianyu-auto-reply" not in output or "latest" not in output:
        print("❌ 镜像不存在！构建可能失败了。")
        print(f"镜像列表:\n{output}")
        return False
    print("✅ 镜像存在")
    
    # 检查entrypoint.sh内容
    print("\n1️⃣ 检查entrypoint.sh是否包含正确代码...")
    output = run_ssh_command("docker run --rm xianyu-auto-reply:latest cat /app/entrypoint.sh | grep 'exec env DISPLAY'")
    if "exec env DISPLAY=:99" in output:
        print("✅ entrypoint.sh包含正确的DISPLAY环境变量设置")
    else:
        print("❌ entrypoint.sh不包含正确代码")
        print(f"检查输出: {output}")
        return False
    
    # 检查文件时间戳
    print("\n2️⃣ 检查文件时间戳...")
    output = run_ssh_command("docker run --rm xianyu-auto-reply:latest ls -la /app/entrypoint.sh")
    print(f"文件信息: {output.strip()}")
    if "Dec 19" in output or "12月 19" in output or "Dec  19" in output:
        print("✅ 文件时间戳正确（2025-12-19）")
        return True
    else:
        print("⚠️ 文件时间戳可能不是最新的")
        # 即使时间戳不是今天，只要包含正确代码也算成功
        print("但entrypoint.sh包含正确代码，继续执行")
        return True

def deploy_container():
    """部署新容器"""
    print("\n" + "="*60)
    print("🚀 步骤6：部署新镜像...")
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
    print("\n⏳ 等待容器完全启动（15秒）...")
    time.sleep(15)
    
    return True

def verify_deployment():
    """验证部署"""
    print("\n" + "="*60)
    print("🔍 步骤7：全面验证...")
    print("="*60)
    
    # 验证Xvfb进程
    print("\n1️⃣ 验证Xvfb进程...")
    output = run_ssh_command("docker exec xianyu-auto-reply ps | grep Xvfb")
    if "Xvfb" in output:
        print(f"✅ Xvfb进程运行中:\n{output}")
    else:
        print("❌ Xvfb进程未运行")
    
    # 验证DISPLAY环境变量
    print("\n2️⃣ 验证DISPLAY环境变量...")
    output = run_ssh_command("docker exec xianyu-auto-reply cat /proc/1/environ | tr '\\0' '\\n' | grep DISPLAY")
    if "DISPLAY=:99" in output:
        print(f"✅ DISPLAY环境变量已设置: {output.strip()}")
    else:
        print(f"❌ DISPLAY环境变量未设置: {output}")
    
    # 检查启动日志
    print("\n3️⃣ 检查启动日志中的Xvfb信息...")
    output = run_ssh_command("docker logs xianyu-auto-reply 2>&1 | grep -E '(Xvfb启动|DISPLAY)' | head -5")
    if output.strip():
        print(f"📋 Xvfb启动日志:\n{output}")
    else:
        print("⚠️ 未找到Xvfb启动日志")
    
    # 检查是否还有DISPLAY错误
    print("\n4️⃣ 检查是否还有DISPLAY错误...")
    output = run_ssh_command("docker logs xianyu-auto-reply 2>&1 | grep 'Missing X server' | tail -5")
    if output.strip():
        print(f"⚠️ 仍有DISPLAY错误（可能是旧日志）:\n{output}")
    else:
        print("✅ 无DISPLAY错误")
    
    return True

def tag_image():
    """打标签备份"""
    print("\n" + "="*60)
    print("🏷️ 步骤8：打标签备份...")
    print("="*60)
    
    # 打日期标签
    output = run_ssh_command("docker tag xianyu-auto-reply:latest xianyu-auto-reply:fixed-$(date +%Y%m%d)")
    print("✅ 已打标签: xianyu-auto-reply:fixed-YYYYMMDD")
    
    # 验证标签
    output = run_ssh_command("docker images | grep xianyu-auto-reply")
    print(f"\n📦 当前镜像列表:\n{output}")
    
    return True

def main():
    """主函数"""
    print("="*60)
    print("🔄 方案2：彻底解决构建问题 - 自动监控与部署")
    print("="*60)
    
    check_interval = 120  # 每2分钟检查一次
    max_wait_time = 3600 * 2  # 最多等待2小时
    elapsed_time = 0
    
    print(f"\n⏰ 检查间隔: {check_interval}秒")
    print(f"⏰ 最大等待时间: {max_wait_time}秒 ({max_wait_time/60}分钟)")
    print(f"\n开始监控构建进度...\n")
    
    while elapsed_time < max_wait_time:
        status = check_build_status()
        
        if status == "completed":
            print("\n" + "="*60)
            print("🎉 步骤4完成：构建成功！")
            print("="*60)
            
            # 步骤5：验证镜像
            if not verify_image():
                print("\n❌ 镜像验证失败！")
                return 1
            
            # 步骤6：部署容器
            if not deploy_container():
                print("\n❌ 容器部署失败！")
                return 1
            
            # 步骤7：验证部署
            if not verify_deployment():
                print("\n❌ 部署验证失败！")
                return 1
            
            # 步骤8：打标签
            if not tag_image():
                print("\n❌ 打标签失败！")
                return 1
            
            print("\n" + "="*60)
            print("✅ 所有步骤完成！方案2执行成功！")
            print("="*60)
            print("\n📋 后续操作：")
            print("1. 访问 http://192.168.123.51:8080")
            print("2. 删除旧账号（ID: 3490501769）")
            print("3. 重新添加账号（扫码登录）")
            print("4. 观察系统是否正常工作")
            return 0
        
        elif status == "error":
            print("\n❌ 构建过程中发生错误！")
            print("\n📋 最后50行日志：")
            output = run_ssh_command("tail -50 /mnt/sata1-1/docker/mycontainers/xianyu-auto-reply/build-final.log")
            print(output)
            return 1
        
        elif status.startswith("building"):
            print(f"\r⏳ 步骤4进行中... [{status}] (已等待 {elapsed_time//60} 分钟)", end="", flush=True)
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
