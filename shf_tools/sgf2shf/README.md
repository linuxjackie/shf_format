# sgf2shf

![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

SGF 轉 SHF 轉換工具

## 功能特點

- 支持批量轉換 SGF 文件到 SHF 格式
- 自動提取級別信息
- 保持原始 SGF 註釋
- 支持多種棋盤大小（9路、13路、19路）

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python sgf2shf.py <input_dir> <output_dir>
```

### 參數說明

- `input_dir`: SGF 文件所在目錄
- `output_dir`: 輸出 SHF 文件的目錄

### 示例

```bash
python sgf2shf.py ./sgf_files ./shf_files
```

## 注意事項

1. 輸入文件必須是有效的 SGF 格式
2. 自動提取的級別信息基於文件名或 SGF 標籤
3. 默認使用 UTF-8 編碼 