import sqlite3

conn = sqlite3.connect('data/geopolitical.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# 查看文章表结构和数据
print("\n=== Articles 表 ===")
cursor.execute("SELECT * FROM articles LIMIT 5")
rows = cursor.fetchall()
print(f"Total articles: {cursor.execute('SELECT COUNT(*) FROM articles').fetchone()[0]}")
for row in rows:
    print(row)

# 查看分析结果表
print("\n=== Analyses 表 ===")
cursor.execute("SELECT * FROM analyses LIMIT 5")
rows = cursor.fetchall()
print(f"Total analyses: {cursor.execute('SELECT COUNT(*) FROM analyses').fetchone()[0]}")
for row in rows[:3]:
    print(row)

conn.close()
