# sqlite2shf

![Version](https://img.shields.io/badge/version-0.9.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

SQLite 數據庫轉 SHF 工具

## 功能特點

- 支持從 SQLite 數據庫導出到 SHF 格式
- 支持選擇性導出（按級別、ID 範圍等）
- 保持數據完整性
- 自動驗證輸出格式

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python sqlite2shf.py <input_db> <output_dir> [options]
```

### 參數說明

- `input_db`: 輸入的 SQLite 數據庫文件
- `output_dir`: 輸出 SHF 文件的目錄
- `options`: 可選參數
  - `--level`: 指定級別（例如：1d, 2k）
  - `--range`: 指定 ID 範圍（例如：1-100）

### 示例

```bash
python sqlite2shf.py ./problems.db ./shf_files --level 1d
```

## 輸出格式

- 每個題目保存為獨立的 SHF 文件
- 文件名格式：`[level][id].shf`
- 內容格式符合 SHF 規範

## 注意事項

1. 自動檢查輸出目錄
2. 支持覆蓋現有文件
3. 默認使用 UTF-8 編碼 