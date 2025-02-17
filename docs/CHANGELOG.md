# 版本記錄

所有重要的更改都會記錄在此文件中。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
並且本項目遵循 [語義化版本](https://semver.org/lang/zh-TW/)。

## [Unreleased]

### 待改進
- 添加更多的單元測試用例
- 完善錯誤處理機制
- 添加性能測試

## [0.9.0] - 2024-02-18

### 新增
- 完整的命令行界面支持
- 批量處理功能
- 詳細的錯誤報告機制
- 完整的中文本地化支持

### 改進
- 優化了轉換性能
- 改進了錯誤處理機制
- 完善了文檔說明
- 增強了代碼健壯性

## [0.8.0] - 2024-02-18

### 新增
- 添加了 SQLite 數據庫索引優化
- 實現了數據庫遷移功能
- 添加了數據導出功能
- 支持自定義配置文件

### 改進
- 優化了數據庫查詢性能
- 改進了內存使用效率
- 完善了錯誤日誌記錄

## [0.7.0] - 2024-02-18

### 新增
- 實現了高級搜索功能
- 添加了數據驗證層
- 支持多種輸出格式
- 添加了進度顯示功能

### 改進
- 優化了搜索算法
- 改進了數據驗證機制
- 增強了錯誤提示

## [0.6.0] - 2024-02-18

### 新增
- 添加了配置文件支持
- 實現了插件系統
- 添加了緩存機制
- 支持自定義輸出格式

### 改進
- 優化了配置管理
- 改進了插件加載機制
- 完善了緩存策略

## [0.5.0] - 2024-02-18

### 新增
- 添加了並行處理支持
- 實現了異步 IO 操作
- 添加了進度報告功能
- 支持斷點續傳

### 改進
- 優化了處理速度
- 改進了資源利用
- 增強了穩定性

## [0.4.0] - 2024-02-18

### 改進
- 重新組織了項目文件結構，使其更加清晰和易於維護
- 優化了文件夾分類和命名
- 更新了文檔，使其更加清晰易懂
- 完善了項目結構說明
- 更新了所有 GitHub 相關連結

## [0.3.0] - 2024-02-17

### 新增
- 在 SHF 格式中添加了注釋功能
  - 添加了初始局面注釋
  - 添加了答案序列注釋

### 改進
- 統一使用 `#` 作為所有注釋的分隔符
  - 初始注釋現在使用 `#` 而不是 `:`
  - 保持格式的一致性和可讀性
- 完善了測試用例
  - 添加了注釋相關的測試
  - 添加了格式驗證測試
  - 添加了座標驗證測試

## [0.2.0] - 2024-02-17

### 改進
- 優化了依賴管理，將運行時依賴和開發依賴分離
- 添加了代碼質量工具（black、flake8、mypy）
- 添加了完整的測試框架和 CI/CD 配置
- 新增了示例文件

### 開發工具
- 新增 test_requirements.txt 用於開發依賴
- 配置了 GitHub Actions 進行自動化測試
- 添加了代碼覆蓋率報告

## [0.1.0] - 2024-02-17

### 新增
- 添加了從SHF到SQLite的轉換功能
- 增強了命令行參數支持
- 引入了基本的錯誤檢查機制

## [0.0.1] - 2024-02-16

### 新增
- 初始版本發布
- 基本的 SHF 格式定義
- 基礎文檔結構

[Unreleased]: https://github.com/linuxjackie/shf_format/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/linuxjackie/shf_format/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/linuxjackie/shf_format/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/linuxjackie/shf_format/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/linuxjackie/shf_format/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/linuxjackie/shf_format/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/linuxjackie/shf_format/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/linuxjackie/shf_format/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/linuxjackie/shf_format/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/linuxjackie/shf_format/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/linuxjackie/shf_format/releases/tag/v0.0.1
