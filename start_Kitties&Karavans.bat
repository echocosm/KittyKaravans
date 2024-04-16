@echo off
REM start_docketeer.bat

REM Change directory to the script location
cd /d %~dp0

REM Set Python version
set PYTHON_VERSION=310

REM Set the process name
set PROCESS_NAME=python.exe

REM Check if another instance is running and end it
tasklist /FI "IMAGENAME eq %PROCESS_NAME%" /FI "WINDOWTITLE eq Docketeer*" 2>NUL | find /I "%PROCESS_NAME%">NUL
if "%ERRORLEVEL%"=="0" (
    echo Another instance of the bot is already running. Ending it...
    for /F "tokens=2 delims=," %%A in ('tasklist /NH /FI "IMAGENAME eq %PROCESS_NAME%" /FI "WINDOWTITLE eq Kitties^&Karavans*"') do (
        taskkill /F /PID %%A
    )
    echo Existing instance terminated.
    goto :continue
)

:continue

REM Check if the virtual environment exists, and create and activate if not
call venv\Scripts\activate || python -m venv venv && call venv\Scripts\activate

REM Upgrade pip and Install dependencies
set "PACKAGES=pip mss opencv-python pynput requests python-dotenv Pillow pystray plyer discord pydirectory reactionmenu"
for %%i in (%PACKAGES%) do (
    python -c "import %%i" >nul 2>nul || (
        python -m pip install --upgrade %%i >nul 2>nul
    )
)
REM Change directory to the bot location
cd /d "%~dp0" 2>nul

REM Run the bot with specified Python version
C:\Users\oakne\AppData\Local\Programs\Python\Python%PYTHON_VERSION%\python.exe Kitties^&Karavans.py

REM Pause to keep the command prompt window open in case of errors
pause
