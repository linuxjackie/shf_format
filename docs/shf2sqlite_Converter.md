```markdown
# shf2sqlite Converter

將SHF（Si Huo Format）格式的圍棋死活題轉換為SQLite數據庫的工具。

## 安裝

確保你的環境中已安裝Python 3.x，無需額外依賴。

## 使用方法

1. **克隆本倉庫**:
   ```bash
   git clone https://github.com/linuxjackie/shf_format
   cd shf_format
   ```

2. **運行轉換器**:

   - 從命令行提供SHF內容:
     ```bash
     echo "00001:1:Baa,Wab,Bac,Wbc:+Bbb,Bbc,Bcc:-Bbb,Bba:/Bbb,Bbc,Bcc," | python shf2sqlite.py
     ```

   - 或者，從文件中讀取SHF內容（假設文件名為`problems.shf`）:
     ```bash
     python shf2sqlite.py < problems.shf
     ```

   - 轉換後的數據將存儲在`go_problems.db`中。

## 代碼

以下是`shf2sqlite.py`的內容：

```python
import sqlite3

def create_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS go_problems (
            id TEXT PRIMARY KEY,
            size INTEGER,
            setup TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS go_solutions (
            solution_id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id TEXT,
            answer TEXT,
            status TEXT,
            FOREIGN KEY (problem_id) REFERENCES go_problems(id)
        )
    ''')
    
    conn.commit()
    return conn, cursor

def shf_to_sqlite(shf_lines, db_path):
    conn, cursor = create_database(db_path)
    
    for line in shf_lines:
        parts = line.strip().split(':')
        problem_id = parts[0]
        size = int(parts[1])
        setup = parts[2]
        
        cursor.execute('INSERT OR REPLACE INTO go_problems (id, size, setup) VALUES (?, ?, ?)', 
                       (problem_id, size, setup))
        
        solutions = ':'.join(parts[3:]).rstrip(',')
        for solution in solutions.split(':'):
            if solution.startswith('+'):
                status = 'correct'
                answer = solution[1:]
            elif solution.startswith('-'):
                status = 'wrong'
                answer = solution[1:]
            elif solution.startswith('/'):
                status = 'variation'
                answer = solution[1:]
            else:
                continue
            
            cursor.execute('INSERT INTO go_solutions (problem_id, answer, status) VALUES (?, ?, ?)',
                           (problem_id, answer, status))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import sys
    shf_lines = sys.stdin.readlines() if not sys.stdin.isatty() else sys.argv[1].split('\n') if len(sys.argv) > 1 else []
    db_path = "go_problems.db"
    shf_to_sqlite(shf_lines, db_path)
    print(f"Data has been written to {db_path}")
```

## 數據庫結構

- **go_problems**:
  - `id` (TEXT): 問題ID，主鍵
  - `size` (INTEGER): 棋盤大小（1=9x9, 2=13x13, 3=19x19）
  - `setup` (TEXT): 初始棋盤狀態

- **go_solutions**:
  - `solution_id` (INTEGER): 自增主鍵
  - `problem_id` (TEXT): 外鍵，參考go_problems表的id
  - `answer` (TEXT): 解答序列
  - `status` (TEXT): 解答狀態（correct, wrong, variation）

## 注意

- 這個工具假設輸入的SHF格式是正確的，沒有進行大量的錯誤檢查。
- 數據庫文件名固定為`go_problems.db`，可以根據需要修改。

## 貢獻

歡迎任何形式的貢獻，包括但不限於錯誤修復、功能增強、文檔改進等。請先開一個議題討論你的改動。
```
