import paramiko

# 读取密码
with open(r'e:\Qoder_workspace\xianyu-auto-reply\password.txt', 'r') as f:
    ip, user, password = f.readline().strip().split()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(ip, username=user, password=password, timeout=10)
    
    # 写入临时 Python 脚本到容器
    script_content = """import sqlite3
conn = sqlite3.connect('/app/data/xianyu_data.db')
cursor = conn.cursor()

# 更新 show_browser
cursor.execute("UPDATE cookies SET show_browser = 0 WHERE id = '行动派do'")
conn.commit()

# 验证
cursor.execute("SELECT id, show_browser FROM cookies WHERE id = '行动派do'")
row = cursor.fetchone()
if row:
    print(f"✅ 账号: {row[0]}, show_browser 已设置为: {row[1]}")
else:
    print("❌ 未找到账号")

conn.close()
"""
    
    # 将脚本写入容器的临时文件
    stdin, stdout, stderr = ssh.exec_command(
        f"docker exec xianyu-auto-reply sh -c 'cat > /tmp/update_db.py << \"EOF\"\n{script_content}\nEOF'"
    )
    stdout.read()
    
    # 执行脚本
    stdin, stdout, stderr = ssh.exec_command("docker exec xianyu-auto-reply python3 /tmp/update_db.py")
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    print(output)
    if error:
        print(f"错误: {error}")
    
    # 清理临时文件
    ssh.exec_command("docker exec xianyu-auto-reply rm /tmp/update_db.py")
    
except Exception as e:
    print(f"❌ 操作失败: {e}")
finally:
    ssh.close()
