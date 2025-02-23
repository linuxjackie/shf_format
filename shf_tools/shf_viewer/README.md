# shf_viewer

![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

SHF 格式題目查看器

## 功能特點

- 互動式圍棋題目界面
- 支持答案驗證
- 多種棋盤大小顯示（9路、13路、19路）
- 支持批註和變化顯示

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python shf_viewer.py [file_or_dir]
```

### 參數說明

- `file_or_dir`: SHF 文件或目錄路徑（可選）
  - 如果是文件，直接打開該題目
  - 如果是目錄，顯示題目列表

### 快捷鍵

- `Space`: 顯示下一步
- `Backspace`: 返回上一步
- `R`: 重置當前題目
- `N`: 下一題
- `P`: 上一題
- `Q`: 退出程序

## 界面功能

1. 棋盤顯示區
   - 顯示當前局面
   - 支持鼠標點擊落子
   
2. 信息面板
   - 顯示題目信息（級別、編號、大小）
   - 答案序列
   - 注釋內容

3. 控制面板
   - 導航按鈕
   - 答案驗證
   - 變化切換

## 文件格式要求

- 支持標準 SHF 格式
- 文件名格式：`[level][id].shf`
- 編碼：UTF-8
- 換行：Unix 風格（LF）

## 注意事項

1. 支持拖放文件
2. 自動保存最近打開的文件
3. 支持主題切換
4. 座標顯示使用小寫字母（a-t，跳過 i） 