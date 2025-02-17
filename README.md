# SHF (Si Huo Format) 死活題格式

![Version](https://img.shields.io/badge/version-0.9.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
[![Tests](https://github.com/linuxjackie/shf_format/workflows/Python%20Tests/badge.svg)](https://github.com/linuxjackie/shf_format/actions)
[![codecov](https://codecov.io/gh/linuxjackie/shf_format/branch/main/graph/badge.svg)](https://codecov.io/gh/linuxjackie/shf_format)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

SHF是一種專為記錄圍棋死活題而設計的高效、簡潔的文本格式。以下是SHF格式的詳細定義：

## 格式概述

SHF格式使用冒號`:`作為主要的分隔符，並設計成一行表示一個完整的圍棋死活題。其主要組成部分包括：

- **ID**（問題唯一識別碼）
- **棋盤大小**（以數字1、2、3表示9路、13路、19路棋盤）
- **初始狀態**（棋盤初始布局）
- **初始注釋**（對初始局面的說明）
- **答案序列**（包含多個可能的解答，帶有正確性標識）
- **答案注釋**（對答案的補充說明）

## 格式結構

```
ID:棋盤大小:初始狀態#初始注釋:+答案序列1#注釋1:-答案序列2#注釋2:/答案序列3#注釋3,
```

### 各部分詳解：

- **ID**：
  - 一個5位數的字符串，用於唯一識別每個問題。例如：`00001`。

- **棋盤大小**：
  - 使用單一數字來表示：
    - `1` 表示 9x9 棋盤
    - `2` 表示 13x13 棋盤
    - `3` 表示 19x19 棋盤

- **初始狀態**：
  - 描述棋盤的初始布局，格式為`B座標,W座標,B座標,W座標,...`：
    - `B`代表黑棋，`W`代表白棋，後面跟隨棋盤座標（如`aa`, `ab`等）。

- **初始注釋**：
  - 對初始局面的說明文字，例如：`黑先活`、`黑先白死`等。
  - 如果沒有注釋，使用空字符串`""`。

- **答案序列**：
  - 每個答案序列由以下部分組成：
    - 前置符號：`+`（正確答案）、`-`（錯誤答案）、`/`（變化或可選答案）
    - 棋步序列：如`Baa,Bbb,Bcc`
    - 注釋標記：`#`
    - 答案注釋：對該答案序列的說明，如`這樣黑棋可以活`
  - 答案步驟用逗號分隔，沒有空格。

### 範例

以下是一個包含注釋的SHF格式示例：

```
00001:1:Baa,Wab,Bac,Wbc#黑先活:+Bbb,Wbc,Bcc#這樣黑棋可以活:-Bbb,Wba#這樣下會被白吃掉:/Bbb,Wbc,Bcc#另一種活棋變化,
```

- **ID**: `00001`
- **棋盤大小**: `1`（表示9路棋盤）
- **初始狀態和注釋**: `Baa,Wab,Bac,Wbc#黑先活`
- **答案序列和注釋**:
  - `+Bbb,Bbc,Bcc#這樣黑棋可以活` 正確答案及其說明
  - `-Bbb,Bba#這樣下會被白吃掉` 錯誤答案及其說明
  - `/Bbb,Bbc,Bcc#另一種活棋變化` 變化或可選答案及其說明

## 使用建議

- 為了保持一致性，請確保所有的ID為5位數，並使用0填充不足5位的ID。
- 棋盤座標遵循圍棋慣例，從左下角開始，a1表示左下角，s19表示右上角（僅適用於19路棋盤）。

## 解析與應用

解析SHF格式的代碼應能夠處理：
- 每個部分的分隔
- 棋盤大小的映射
- 初始狀態和答案序列的轉換

## FAQ

**Q: 如何處理大量的SHF文件？**

A: 你可以編寫一個腳本來批量處理多個SHF文件，或者直接從命令行連續輸入多個SHF內容。

**Q: 如果我遇到ID衝突怎麼辦？**

A: 目前腳本會用`INSERT OR REPLACE`來處理ID衝突，但你可以修改為`INSERT OR IGNORE`或添加一個唯一性檢查前置步驟。

**Q: 如何處理SHF格式中的錯誤？**

A: 本腳本會嘗試檢查SHF格式的正確性，但如果你遇到無法解釋的錯誤，請檢查你的SHF內容是否符合格式規範或報告問題。

## 項目結構

```
shf_format/
│
├── 核心程式/
│   ├── sgf2shf.py      # SGF 轉 SHF 格式轉換器
│   └── shf2sqlite.py   # SHF 轉 SQLite 數據庫轉換器
│
├── 測試/
│   ├── test_sgf2shf.py    # SGF 轉換器的單元測試
│   └── test_shf2sqlite.py # SQLite 轉換器的單元測試
│
├── 示例/
│   ├── sample.sgf  # SGF 格式示例文件
│   └── sample.shf  # SHF 格式示例文件
│
├── 文檔/
│   ├── README.MD        # 項目主要文檔
│   ├── CHANGELOG.md     # 版本更新記錄
│   └── CONTRIBUTING.md  # 貢獻指南
│
├── 配置文件/
│   ├── requirements.txt      # 基本依賴包列表
│   ├── test_requirements.txt # 測試依賴包列表
│   ├── setup.py             # 包安裝配置
│   └── .gitignore           # Git 忽略文件配置
│
└── CI配置/
    └── .github/
        └── workflows/
            └── python-app.yml # GitHub Actions CI 配置
```

## 安裝

### 使用 pip 安裝（推薦）

```bash
# 安裝基本版本
pip install shf-format

# 安裝開發版本（包含所有開發工具）
pip install shf-format[dev]
```

### 從源碼安裝

1. 克隆倉庫：
```bash
git clone https://github.com/linuxjackie/shf_format.git
cd shf_format
```

2. 安裝依賴：
```bash
# 安裝基本依賴
pip install -r requirements.txt

# 或安裝開發依賴
pip install -r test_requirements.txt
```

3. 安裝包：
```bash
# 安裝為可編輯模式（推薦開發者使用）
pip install -e .

# 或直接安裝
pip install .
```

## 開發

### 代碼品質

本項目使用以下工具來確保代碼品質：

- **black**: 代碼格式化
- **flake8**: 代碼風格檢查
- **mypy**: 類型檢查

運行代碼品質檢查：

```bash
# 格式化代碼
black .

# 代碼風格檢查
flake8 .

# 類型檢查
mypy .
```

### 運行測試

本項目使用 pytest 進行測試。要運行測試，請執行：

```bash
pytest tests/
```

要查看測試覆蓋率報告：

```bash
pytest tests/ --cov=./ --cov-report=html
```

### 貢獻

1. Fork 本倉庫
2. 創建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

更多詳情請參見 [CONTRIBUTING.md](https://github.com/linuxjackie/shf_format/blob/main/CONTRIBUTING.md)。

## 快速開始

### 轉換 SGF 到 SHF

```bash
# 轉換單個文件
python sgf2shf.py input.sgf output.shf

# 批量轉換目錄
python sgf2shf.py --input-dir ./sgf_files --output-dir ./shf_files

# 顯示幫助
python sgf2shf.py --help
```

### 轉換 SHF 到 SQLite

```bash
# 轉換單個文件
python shf2sqlite.py input.shf output.db

# 批量轉換目錄
python shf2sqlite.py --input-dir ./shf_files --output-db output.db

# 顯示幫助
python shf2sqlite.py --help
```

### 命令行參數

#### sgf2shf.py

```
選項：
  -i, --input FILE     輸入的 SGF 文件
  -o, --output FILE    輸出的 SHF 文件
  --input-dir DIR      輸入目錄（批量轉換）
  --output-dir DIR     輸出目錄（批量轉換）
  -v, --verbose        顯示詳細信息
  -h, --help          顯示幫助信息
```

#### shf2sqlite.py

```
選項：
  -i, --input FILE     輸入的 SHF 文件
  -o, --output FILE    輸出的 SQLite 數據庫文件
  --input-dir DIR      輸入目錄（批量轉換）
  --output-db FILE     輸出數據庫文件（批量轉換）
  --replace           替換已存在的記錄
  --ignore            忽略已存在的記錄
  -v, --verbose        顯示詳細信息
  -h, --help          顯示幫助信息
```
