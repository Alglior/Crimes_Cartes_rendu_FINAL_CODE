@echo off
setlocal enabledelayedexpansion

:: Set the name of your virtual environment
set VENV_NAME=myenv

:: Set the name of your Python script
set SCRIPT_NAME=map_categorie.py

echo [DEBUG] Starting script execution...

:: Check if virtual environment exists
if not exist %VENV_NAME%\Scripts\activate.bat (
    echo [ERROR] Virtual environment not found. Please create it first.
    goto :error
)

:: Activate the virtual environment
echo [DEBUG] Activating virtual environment...
call %VENV_NAME%\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment. Error code: %errorlevel%
    goto :error
)

:: Run the Python script
echo [DEBUG] Running %SCRIPT_NAME%...
python %SCRIPT_NAME%
if %errorlevel% neq 0 (
    echo [ERROR] Failed to run %SCRIPT_NAME%. Error code: %errorlevel%
    goto :error
)

:: Deactivate the virtual environment
echo [DEBUG] Deactivating virtual environment...
deactivate

echo [SUCCESS] Script execution completed successfully.
goto :end

:error
echo [ERROR] An error occurred during script execution.
echo [ERROR] Please check the error messages above for more information.

:end
echo [DEBUG] Script process finished.
pause
