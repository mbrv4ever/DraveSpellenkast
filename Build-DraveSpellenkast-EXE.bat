@echo off
title DraveSpellenkast - EXE bouwen
rem Copyright (C) 2026 Dravenlock (Roger ^& Claudio). GNU GPL v3.0.
cd /d "%~dp0"
set "APPN=DraveSpellenkast"
set "DATA=dist\%APPN%\%APPN%-data"
set "RESERVE=D:\Caches\%APPN%_data_reserve"
if exist "%DATA%" ( if exist "%RESERVE%" rmdir /s /q "%RESERVE%" & robocopy "%DATA%" "%RESERVE%" /e /njh /njs /nfl /ndl >nul )
py -3.10 make_icon.py || goto mislukt
py -3.10 -m PyInstaller --noconfirm --clean --windowed --onedir --name %APPN% --icon "%~dp0assets\icon.ico" --hidden-import bg_regels --hidden-import topo --hidden-import vier --hidden-import zeeslag --hidden-import wiebenik --hidden-import dammen --hidden-import schaken --hidden-import galgje --hidden-import memory --hidden-import lingo --hidden-import reversi --hidden-import domino --hidden-import ganzenbord --hidden-import pesten --hidden-import puzzel --hidden-import sudoku --hidden-import duel --hidden-import online --collect-submodules websockets --exclude-module tkinter main.py
if errorlevel 1 goto mislukt
if not exist "dist\%APPN%\%APPN%.exe" ( echo GEEN EXE GEVONDEN & goto mislukt )
xcopy /e /i /y assets "dist\%APPN%\assets" >nul
if exist "%RESERVE%" robocopy "%RESERVE%" "%DATA%" /e /njh /njs /nfl /ndl >nul
rmdir /s /q build 2>nul
del /q %APPN%.spec 2>nul
echo KLAAR: dist\%APPN%\%APPN%.exe
exit /b 0
:mislukt
echo BOUWEN MISLUKT
exit /b 1
