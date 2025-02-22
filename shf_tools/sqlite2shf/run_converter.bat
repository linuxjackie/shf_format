@echo off
setlocal enabledelayedexpansion

:: 設置日誌目錄
set "LOG_DIR=logs"
set "LOG_FILE=%LOG_DIR%\startup.log"

:: 創建日誌目錄（如果不存在）
if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
    echo %date% %time% - 創建日誌目錄 >> "%LOG_FILE%"
)

:: 清理舊的日誌文件
echo. > "%LOG_FILE%"

:: 記錄啟動信息
echo %date% %time% - 啟動 SQLite to SHF 轉換器... >> "%LOG_FILE%"
echo %date% %time% - 工作目錄: %CD% >> "%LOG_FILE%"

:: 檢查 Python 環境
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo %date% %time% - 錯誤: 未找到 Python >> "%LOG_FILE%"
    echo 錯誤: 請確保已安裝 Python 並添加到系統路徑中
    pause
    exit /b 1
)

:: 檢查虛擬環境
if not exist "venv" (
    echo %date% %time% - 創建虛擬環境... >> "%LOG_FILE%"
    python -m venv venv
    if %errorlevel% neq 0 (
        echo %date% %time% - 錯誤: 創建虛擬環境失敗 >> "%LOG_FILE%"
        echo 錯誤: 創建虛擬環境失敗
        pause
        exit /b 1
    )
    
    echo %date% %time% - 安裝依賴... >> "%LOG_FILE%"
    call venv\Scripts\activate
    pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
    if %errorlevel% neq 0 (
        echo %date% %time% - 錯誤: 安裝依賴失敗 >> "%LOG_FILE%"
        echo 錯誤: 安裝依賴失敗，請查看日誌文件了解詳情
        pause
        exit /b 1
    )
) else (
    call venv\Scripts\activate
)

:: 運行轉換器
echo %date% %time% - 運行轉換器... >> "%LOG_FILE%"
python src\main.py >> "%LOG_FILE%" 2>&1

if %errorlevel% neq 0 (
    echo %date% %time% - 錯誤: 運行失敗 >> "%LOG_FILE%"
    echo 錯誤: 程序運行失敗，請查看日誌文件了解詳情
    echo 日誌文件位置: %LOG_FILE%
) else (
    echo %date% %time% - 程序正常結束 >> "%LOG_FILE%"
)

pause 