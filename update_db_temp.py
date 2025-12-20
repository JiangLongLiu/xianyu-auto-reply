import sqlite3

conn = sqlite3.connect('/app/data/xianyu_data.db')
cursor = conn.cursor()

# 先查询所有账号
print("📋 数据库中的所有账号:")
cursor.execute("SELECT id, show_browser FROM cookies")
for row in cursor.fetchall():
    print(f"  - 账号: {row[0]}, show_browser: {row[1]}")

# 更新所有账号的 show_browser
print("\n🔧 更新所有账号的 show_browser 为 0...")
cursor.execute("UPDATE cookies SET show_browser = 0")
conn.commit()
print(f"✅ 已更新 {cursor.rowcount} 个账号")

# 验证
print("\n✔️ 验证更新结果:")
cursor.execute("SELECT id, show_browser FROM cookies")
for row in cursor.fetchall():
    print(f"  - 账号: {row[0]}, show_browser: {row[1]}")

conn.close()
