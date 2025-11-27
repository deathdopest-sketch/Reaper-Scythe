@echo off
REM Windows build script for Reaper executable
REM Usage: build.bat [package|installer|sign]
REM   package   - Full release package (build + installer + checksums)
REM   installer - Build + create installer
REM   sign      - Build + sign executable
REM   (no args) - Build only

set MODE=%1
if "%MODE%"=="" set MODE=build

echo Building Reaper executable for Windows...
echo Mode: %MODE%

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Check if Nuitka is installed
python -m nuitka --version >nul 2>&1
if errorlevel 1 (
    echo Installing Nuitka...
    python -m pip install nuitka
)

if "%MODE%"=="package" (
    REM Full release package
    python package.py
    if errorlevel 1 exit /b 1
) else if "%MODE%"=="installer" (
    REM Build + installer
    python nuitka_build.py
    if errorlevel 1 exit /b 1
    python -m packaging.installers Windows
    if errorlevel 1 exit /b 1
) else if "%MODE%"=="sign" (
    REM Build + sign
    python nuitka_build.py
    if errorlevel 1 exit /b 1
    if defined WINDOWS_CERT_PATH (
        python -m packaging.signing dist\reaper.exe
    ) else (
        echo Warning: WINDOWS_CERT_PATH not set, skipping signing
    )
) else (
    REM Build only
    python nuitka_build.py
    if errorlevel 1 (
        echo Build failed!
        exit /b 1
    ) else (
        echo Build completed successfully!
        echo Executable: dist\reaper.exe
    )
)

