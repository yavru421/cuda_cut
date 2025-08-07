@echo off
REM Launch CUDA_Cut GUI using venv
cd /d "%~dp0"

REM Set VIRTUAL_ENV variable before any block to avoid scoping issues for CUDA_Cut
set "VIRTUAL_ENV=%CD%\venv"

REM Activate venv and run the CUDA_Cut GUI


if exist "venv\Scripts\activate.bat" goto venv_found
goto venv_not_found

:venv_found
call venv\Scripts\activate.bat
echo Installing/updating requirements...
REM Use python.exe -m pip to avoid pip self-upgrade warning
"%VIRTUAL_ENV%\Scripts\python.exe" -m pip install --upgrade pip
"%VIRTUAL_ENV%\Scripts\pip.exe" install -r requirements.txt

echo Checking for ffplay (ffmpeg)...
where ffplay >nul 2>nul
if %errorlevel% neq 0 goto warn_ffplay

echo Checking rembg and onnxruntime-gpu...
"%VIRTUAL_ENV%\Scripts\pip.exe" show rembg >nul 2>nul
if %errorlevel% neq 0 goto install_rembg

"%VIRTUAL_ENV%\Scripts\pip.exe" show onnxruntime-gpu >nul 2>nul
if %errorlevel% neq 0 goto install_onnx

"%VIRTUAL_ENV%\Scripts\python.exe" test_cuda.py
"%VIRTUAL_ENV%\Scripts\python.exe" cuda_cut_gui.py
goto end

:venv_not_found
echo CUDA_Cut virtual environment not found! Please set up venv first.
pause
goto end

:warn_ffplay
echo.
echo WARNING: ffplay (from ffmpeg) is not found in your PATH.
echo CUDA_Cut video preview will NOT work until you install ffmpeg and add it to your PATH.
echo Download from: https://ffmpeg.org/download.html
echo Or use: choco install ffmpeg (if you have Chocolatey)
echo.
REM Only pause for user to see warning, then continue
pause
goto continue_checks

:install_rembg
"%VIRTUAL_ENV%\Scripts\pip.exe" install rembg
goto continue_checks

:install_onnx
"%VIRTUAL_ENV%\Scripts\pip.exe" install onnxruntime-gpu
goto continue_checks

:continue_checks
"%VIRTUAL_ENV%\Scripts\python.exe" test_cuda.py
"%VIRTUAL_ENV%\Scripts\python.exe" cuda_cut_gui.py
goto end

:end
