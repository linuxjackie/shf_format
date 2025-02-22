@echo off
setlocal EnableDelayedExpansion

:: 保存當前目錄
set "SCRIPT_DIR=%~dp0"
set "LOG_DIR=%SCRIPT_DIR%logs"

:: 清除現有日誌文件
echo 清除現有日誌文件...
if exist "%LOG_DIR%" (
    del /F /Q "%LOG_DIR%\*.*"
) else (
    mkdir "%LOG_DIR%"
)

:: 設置日誌文件
set "LOG_FILE=%LOG_DIR%\startup.log"

echo 啟動時間: %date% %time% > "%LOG_FILE%"
echo 工作目錄: %SCRIPT_DIR% >> "%LOG_FILE%"

echo 正在檢查 Python 環境...
python --version >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo 錯誤：未找到 Python，請確保已安裝 Python 3.8 或更高版本
    echo Python 檢查失敗 >> "%LOG_FILE%"
    type "%LOG_FILE%"
    pause
    exit /b
)

:: 檢查虛擬環境
if not exist "%SCRIPT_DIR%venv" (
    echo 創建虛擬環境...
    echo 創建虛擬環境... >> "%LOG_FILE%"
    python -m venv "%SCRIPT_DIR%venv" >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo 創建虛擬環境失敗！
        echo 虛擬環境創建失敗 >> "%LOG_FILE%"
        type "%LOG_FILE%"
        pause
        exit /b
    )
)

:: 激活虛擬環境
echo 激活虛擬環境... >> "%LOG_FILE%"
call "%SCRIPT_DIR%venv\Scripts\activate.bat"

:: 安裝依賴
echo 正在檢查並安裝依賴...
echo 安裝依賴... >> "%LOG_FILE%"
python -m pip install --upgrade pip >> "%LOG_FILE%" 2>&1
pip install PyQt6 >> "%LOG_FILE%" 2>&1

:: 檢查安裝
python -c "import PyQt6" 2>> "%LOG_FILE%"
if errorlevel 1 (
    echo PyQt6 安裝失敗！
    echo PyQt6 安裝失敗 >> "%LOG_FILE%"
    type "%LOG_FILE%"
    pause
    exit /b
)

:: 運行程序
echo 啟動 SHF Viewer...
echo 啟動應用程序... >> "%LOG_FILE%"
cd /d "%SCRIPT_DIR%src"
python main.py >> "%LOG_FILE%" 2>&1

if errorlevel 1 (
    echo 程序執行出錯！
    echo.
    echo === 錯誤日誌開始 ===
    type "%LOG_FILE%"
    echo === 錯誤日誌結束 ===
    echo.
    echo 完整日誌文件位置：
    echo %LOG_FILE%
    echo %LOG_DIR%\shf_viewer.log
    pause
)

:: 退出虛擬環境
deactivate
endlocal 