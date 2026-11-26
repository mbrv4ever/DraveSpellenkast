@echo off
title DraveSpellenkast
rem Copyright (C) 2026 Dravenlock (Roger ^& Claudio). GNU GPL v3.0.
cd /d "%~dp0"
set PY=
for %%V in (3.10 3.12 3.11) do if not defined PY py -%%V -c "import pygame,numpy" >nul 2>&1 && set PY=py -%%V
if not defined PY ( echo Geen Python met pygame en numpy gevonden. & pause & exit /b 1 )
%PY% main.py
if errorlevel 1 pause
