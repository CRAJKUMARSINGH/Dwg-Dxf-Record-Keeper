@echo off
echo ================================================================================
echo DXF Drawing Pattern Analyzer - Quick Launch
echo ================================================================================
echo.
echo Select an option:
echo.
echo 1. Run DXF Pattern Analysis
echo 2. Run Quick Start Demo (Generate Sample Drawings)
echo 3. Run Drawing Extractor
echo 4. View Summary Report
echo 5. View README Documentation
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Running DXF Pattern Analysis...
    echo.
    python dxf_pattern_analyzer.py
    pause
) else if "%choice%"=="2" (
    echo.
    echo Running Quick Start Demo...
    echo.
    python quick_start_demo.py
    pause
) else if "%choice%"=="3" (
    echo.
    echo Running Drawing Extractor...
    echo.
    echo Usage: python drawing_extractor.py -s [source] -t [target] [--dry-run] [--force]
    echo.
    set /p cmd="Enter command or press Enter to exit: "
    if not "%cmd%"=="" (
        %cmd%
        pause
    )
) else if "%choice%"=="4" (
    echo.
    echo Opening Summary Report...
    start SUMMARY.md
) else if "%choice%"=="5" (
    echo.
    echo Opening README...
    start README.md
) else if "%choice%"=="6" (
    echo.
    echo Exiting...
    exit /b
) else (
    echo.
    echo Invalid choice!
    pause
)
