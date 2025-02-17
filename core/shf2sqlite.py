import sqlite3
import re

def validate_shf_format(shf_line):
    """驗證 SHF 格式是否正確"""
    # 檢查基本結構
    parts = shf_line.strip().split(':')
    if len(parts) != 4:
        raise ValueError("SHF 格式必須包含四個部分")
        
    # 檢查 ID
    if not (parts[0].isdigit() and len(parts[0]) == 5):
        raise ValueError("ID 必須是5位數字")
        
    # 檢查棋盤大小
    if parts[1] not in ['1', '2', '3']:
        raise ValueError("棋盤大小必須是 1、2 或 3")
        
    # 檢查初始狀態和注釋
    initial_part = parts[2]
    if '#' in initial_part:
        state, comment = initial_part.split('#')
        if any(c in comment for c in [':', ',', '#', '\n', '\r']):
            raise ValueError("注釋中包含非法字符")
    else:
        state = initial_part
        
    # 檢查移動格式
    valid_chars = {
        '1': 'abcdefghi',
        '2': 'abcdefghijklm',
        '3': 'abcdefghijklmnopqrs'
    }[parts[1]]
    
    for move in state.split(','):
        if not move:
            continue
        if len(move) != 3 or move[0] not in 'BW' or \
           move[1] not in valid_chars or move[2] not in valid_chars:
            raise ValueError(f"無效的移動格式: {move}")
            
    # 檢查答案序列
    answers = [a for a in parts[3].split(',') if a]
    if not answers:
        raise ValueError("必須至少有一個答案序列")
    if not any(a.startswith('+') for a in answers):
        raise ValueError("必須至少有一個正確答案")
        
    for answer in answers:
        if not answer[0] in ['+', '-', '/']:
            raise ValueError(f"無效的答案類型標記: {answer[0]}")
            
        if '#' in answer:
            moves, comment = answer[1:].split('#')
            if any(c in comment for c in [':', ',', '#', '\n', '\r']):
                raise ValueError("注釋中包含非法字符")
        else:
            moves = answer[1:]
            
        # 檢查移動序列
        moves = moves.split(',')
        if len(moves) > 30:
            raise ValueError("移動序列超過30步限制")
            
        positions = set()
        last_color = None
        for move in moves:
            if not move:
                continue
            if len(move) != 3 or move[0] not in 'BW' or \
               move[1] not in valid_chars or move[2] not in valid_chars:
                raise ValueError(f"無效的移動格式: {move}")
                
            if last_color == move[0]:
                raise ValueError("連續同色落子")
            if move[1:] in positions:
                raise ValueError(f"重複落子: {move[1:]}")
                
            positions.add(move[1:])
            last_color = move[0]
            
    return True

def create_database(db_path):
    """創建數據庫和表結構"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 問題表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS problems (
            id TEXT PRIMARY KEY,
            board_size INTEGER,
            initial_state TEXT,
            initial_comment TEXT
        )
    ''')
    
    # 答案表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solutions (
            solution_id INTEGER PRIMARY KEY AUTOINCREMENT,
            problem_id TEXT,
            sequence TEXT,
            type TEXT CHECK(type IN ('+', '-', '/')),
            comment TEXT,
            FOREIGN KEY (problem_id) REFERENCES problems(id)
        )
    ''')
    
    conn.commit()
    return conn, cursor

def shf_to_sqlite(shf_lines, db_path, replace=True):
    """
    將 SHF 格式轉換為 SQLite 數據庫
    
    :param shf_lines: SHF 格式的行列表
    :param db_path: 數據庫文件路徑
    :param replace: 是否替換已存在的記錄
    """
    conn, cursor = create_database(db_path)
    
    for line in shf_lines:
        # 驗證 SHF 格式
        if not validate_shf_format(line.strip()):
            continue
            
        parts = line.strip().split(':')
        problem_id = parts[0]
        board_size = int(parts[1])
        
        # 處理初始狀態和注釋
        initial_part = parts[2]
        if '#' in initial_part:
            initial_state, initial_comment = initial_part.split('#')
        else:
            initial_state = initial_part
            initial_comment = ""
            
        # 插入問題記錄
        if replace:
            cursor.execute('''
                INSERT OR REPLACE INTO problems (id, board_size, initial_state, initial_comment)
                VALUES (?, ?, ?, ?)
            ''', (problem_id, board_size, initial_state, initial_comment))
        else:
            cursor.execute('''
                INSERT OR IGNORE INTO problems (id, board_size, initial_state, initial_comment)
                VALUES (?, ?, ?, ?)
            ''', (problem_id, board_size, initial_state, initial_comment))
            
        # 如果替換模式，先刪除舊的答案
        if replace:
            cursor.execute('DELETE FROM solutions WHERE problem_id = ?', (problem_id,))
            
        # 處理答案序列
        answers = [a for a in parts[3].split(',') if a]
        for answer in answers:
            answer_type = answer[0]
            if '#' in answer[1:]:
                sequence, comment = answer[1:].split('#')
            else:
                sequence = answer[1:]
                comment = ""
                
            cursor.execute('''
                INSERT INTO solutions (problem_id, sequence, type, comment)
                VALUES (?, ?, ?, ?)
            ''', (problem_id, sequence, answer_type, comment))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Convert SHF format to SQLite database")
    parser.add_argument("-i", "--input", help="Input SHF file")
    parser.add_argument("-o", "--output", default="go_problems.db", help="Output SQLite database file")
    parser.add_argument("--replace", action="store_true", help="Replace existing records")
    parser.add_argument("--ignore", action="store_true", help="Ignore existing records")
    args = parser.parse_args()
    
    if args.input:
        with open(args.input, 'r') as f:
            shf_lines = f.readlines()
    else:
        shf_lines = sys.stdin.readlines()
        
    shf_to_sqlite(shf_lines, args.output, not args.ignore)
    print(f"Data has been written to {args.output}") 