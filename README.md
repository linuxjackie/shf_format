# SHF 格式規範 (Smart Go Format)

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

[English](README_EN.md) | 繁體中文

SHF 是一種用於圍棋死活題的文件格式，專門設計用於存儲和交換圍棋死活題數據。

## 相關工具

所有工具都位於 [shf_tools](shf_tools/) 目錄下：

### [sgf2shf](shf_tools/sgf2shf/) ![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
- SGF 轉 SHF 轉換工具
- 支持批量轉換
- 自動提取級別信息

### [shf2sqlite](shf_tools/shf2sqlite/) ![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
- SHF 轉 SQLite 數據庫工具
- 高效的數據庫存儲
- 支持批量導入

### [sqlite2shf](shf_tools/sqlite2shf/) ![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
- SQLite 數據庫轉 SHF 工具
- 支持選擇性導出
- 保持數據完整性

### [shf_viewer](shf_tools/shf_viewer/) ![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
- SHF 格式題目查看器
- 互動式界面
- 支持答案驗證

## 格式定義

SHF 文件的每一行代表一個死活題，格式如下：

```
level:id:size:initial_positions:answers
```

### 欄位說明

1. `level`: 級別
   - 段位表示：1d-9d
   - 級位表示：1k-30k
   - 未標示級別：00

2. `id`: 題目編號
   - 5位數字，如：00001

3. `size`: 棋盤大小
   - 1：9路盤
   - 2：13路盤
   - 3：19路盤

4. `initial_positions`: 初始局面
   - 格式：`[B|W][a-t][a-t]`（跳過 i）
   - 例如：`Ba1,Wb2,Bc3`
   - 可選：末尾可加注釋，使用#分隔，如：`Ba1,Wb2#這是注釋`

5. `answers`: 答案序列
   - 格式：`[+|-|/][B|W][a-t][a-t](,...)#comment`（跳過 i）
   - +：正確答案
   - -：錯誤答案
   - /：變化
   - 每個答案可以包含多個移動，用逗號分隔
   - 可選：每個答案後可加注釋，使用#分隔

### 示例

基本示例：
```
1d:00001:3:Ba1,Wb2,Bc3:+Ba4,Wb5#正確應對,/Wa4#變化,/Bc5#變化
```

複雜示例（多變化）：
```
2d:00015:3:Ba1,Wb2,Bc3,Wd4#黑先活:+Ba4,Wb5,Bc6#正確應對,+Ba5,Wb6,Bc7#另一種活法,-Bd5#這樣不行,/Wa4,Bb5,Wc6#白的變化
```

更多示例請查看 [examples](examples/) 目錄。

## 格式驗證

以下是一個簡單的 Python 格式驗證器：

```python
import re

def validate_shf(line):
    """驗證 SHF 格式是否正確"""
    # 分割各個部分
    parts = line.strip().split(':')
    if len(parts) != 5:
        return False, "格式錯誤：需要5個部分"
        
    level, id_, size, initial, answers = parts
    
    # 驗證級別
    if not re.match(r'^([1-9]d|[1-3][0-9]?k|00)$', level):
        return False, "級別格式錯誤"
        
    # 驗證ID
    if not re.match(r'^\d{5}$', id_):
        return False, "ID必須是5位數字"
        
    # 驗證棋盤大小
    if size not in ['1', '2', '3']:
        return False, "棋盤大小必須是1、2或3"
        
    # 驗證初始位置
    positions = initial.split('#')[0]
    for pos in positions.split(','):
        if pos and not re.match(r'^[BW][a-hj-t][a-hj-t]$', pos):
            return False, f"無效的位置格式：{pos}"
            
    # 驗證答案
    for ans in answers.split(','):
        if not ans:
            continue
        if '#' in ans:
            ans = ans.split('#')[0]
        if not re.match(r'^[+\-/][BW][a-hj-t][a-hj-t]', ans):
            return False, f"無效的答案格式：{ans}"
            
    return True, "格式正確"

# 使用示例
line = "1d:00001:3:Ba1,Wb2,Bc3:+Ba4,Wb5#正確應對,/Wa4#變化"
is_valid, message = validate_shf(line)
print(message)
```

## 文件命名規範

建議的文件命名格式：`[level][id].shf`
例如：
- `1d00001.shf`
- `2k00015.shf`

## 技術規範

1. 編碼：UTF-8
2. 換行：Unix 風格（LF）
3. 座標系統：
   - a-t 表示 1-19 路（跳過 i）
   - 不使用 i 座標（避免與 l 混淆）
   - 左上角為 a1

## 使用場景

1. 死活題數據庫
2. 圍棋教學軟件
3. 題庫交換
4. 移動應用

## 注意事項

1. 所有座標均使用小寫字母
2. 答案序列末尾需要有逗號
3. 注釋內容不應包含特殊分隔符（:, #）
4. 每個文件可以包含多行，每行一個題目

## 常見問題

**Q: 為什麼選擇冒號作為分隔符？**
A: 冒號在圍棋術語中較少出現，不容易與內容混淆。

**Q: 如何處理超過 99999 的題目？**
A: 建議創建新的文件系列，例如使用字母前綴：a00001, b00001 等。

**Q: 可以在注釋中使用 HTML 標記嗎？**
A: 不建議在注釋中使用任何標記語言，以保持格式的簡潔性。

**Q: 如何處理變化中的多種可能性？**
A: 使用多個 "/" 開頭的答案序列來表示不同的變化。

## 貢獻

歡迎提供改進建議和 bug 報告。請查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何貢獻。

## 版權說明

本格式規範採用 MIT 授權條款。歡迎任何人使用、修改和分發。
