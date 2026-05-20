@echo off

REM Move current directory
cd /d %~dp0

REM Run first application
start "" python disp_realtime_gsp.py

REM Waiting 5 second
timeout /t 5

REM Run second application
start "" python user_request_monitoring.py
