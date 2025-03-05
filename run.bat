@echo off
setlocal enabledelayedexpansion

echo [DEBUG] Starting setup process...

:: Set the name of your virtual environment
set VENV_NAME=myenv

echo [DEBUG] Virtual environment name set to: %VENV_NAME%

:: Create a virtual environment
echo [DEBUG] Creating virtual environment...
python -m venv %VENV_NAME%
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment. Error code: %errorlevel%
    goto :error
)

:: Activate the virtual environment
echo [DEBUG] Activating virtual environment...
call %VENV_NAME%\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment. Error code: %errorlevel%
    goto :error
)

:: Upgrade pip
echo [DEBUG] Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip. Error code: %errorlevel%
    echo [WARNING] Continuing with existing pip version...
)

:: Install required packages
echo [DEBUG] Installing required packages...
pip install pandas folium branca plotly
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages. Error code: %errorlevel%
    goto :error
)

:: Create a Python script with import statements
echo [DEBUG] Creating test import script...
(
echo import pandas as pd
echo import folium 
echo import os
echo from datetime import datetime
echo import branca.colormap as cm
echo import json
echo import plotly.express as px
echo import plotly.io as pio
echo from folium import plugins
echo.
echo print("All packages imported successfully!"^)
) > test_imports.py

:: Run the test script
echo [DEBUG] Running test import script...
python test_imports.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to run test script. Error code: %errorlevel%
    goto :error
)

:: Deactivate the virtual environment
echo [DEBUG] Deactivating virtual environment...
deactivate

echo.
echo [SUCCESS] Environment setup complete. To activate the environment, use:
echo %VENV_NAME%\Scripts\activate.bat

goto :end

:error
echo [ERROR] An error occurred during the setup process.
echo [ERROR] Please check the error messages above for more information.

:end
echo [DEBUG] Setup process finished.
pause
