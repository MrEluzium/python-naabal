@ECHO OFF

setlocal

:: get script directory
set PYTHONPATH=%~dp0
IF %PYTHONPATH:~-1%==\ SET PYTHONPATH=%PYTHONPATH:~0,-1%

set PATH=%PYTHONPATH%;%PYTHONPATH%\Scripts;%PATH%

:: compiler for pip
if exist "%VS120COMNTOOLS%" @set VS90COMNTOOLS=%VS120COMNTOOLS%
if exist "%VS110COMNTOOLS%" @set VS90COMNTOOLS=%VS110COMNTOOLS%
if exist "%VS100COMNTOOLS%" @set VS90COMNTOOLS=%VS100COMNTOOLS%
::@if exists "%VS90COMNTOOLS%" @set VS90COMNTOOLS=%VS110COMNTOOLS%

cd /d %USERPROFILE%
call %COMSPEC%

