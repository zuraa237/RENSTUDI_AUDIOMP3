@echo off
cd /d "%~dp0"
where python >nul 2>nul || (echo Python belum terpasang. Install Python 3.10+ dulu.&pause&exit /b 1)
where ffmpeg >nul 2>nul || (echo FFmpeg belum ada di PATH. Install FFmpeg dulu.&pause&exit /b 1)
python -m pip install -r requirements.txt
python server.py
pause
