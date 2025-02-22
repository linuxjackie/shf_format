# shf2sqlite

![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

SHF 轉 SQLite 數據庫工具

## 功能特點

- 支持批量導入 SHF 文件到 SQLite 數據庫
- 高效的數據庫存儲結構
- 支持數據完整性檢查
- 自動創建索引優化查詢性能

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python shf2sqlite.py <input_dir> <output_db>
```

### 參數說明

- `input_dir`: SHF 文件所在目錄
- `output_db`: 輸出的 SQLite 數據庫文件名

### 示例

```bash
python shf2sqlite.py ./shf_files ./problems.db
```

## 數據庫結構

```sql
CREATE TABLE problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT NOT NULL,           -- 1d-9d, 1k-30k, 00
    problem_id TEXT NOT NULL,      -- 5位數字
    board_size INTEGER NOT NULL,   -- 1=9路, 2=13路, 3=19路
    initial_position TEXT NOT NULL, -- 初始局面，包含注釋
    answers TEXT NOT NULL,         -- 答案序列，包含注釋
    file_name TEXT NOT NULL,       -- 原始文件名
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_level ON problems(level);
CREATE INDEX idx_problem_id ON problems(problem_id);
CREATE INDEX idx_board_size ON problems(board_size);
CREATE UNIQUE INDEX idx_level_problem_id ON problems(level, problem_id);
```

## 格式要求

1. 輸入文件必須符合 SHF 格式規範：
   - 文件名格式：`[level][id].shf`
   - 編碼：UTF-8
   - 換行：Unix 風格（LF）

2. 數據驗證：
   - 級別格式：1d-9d, 1k-30k, 00
   - 題目編號：5位數字
   - 棋盤大小：1, 2, 3
   - 座標格式：小寫 a-s（不使用 i）

## 注意事項

1. 自動備份現有數據庫
2. 支持增量更新
3. 默認使用 UTF-8 編碼
4. 保持注釋中的換行符 