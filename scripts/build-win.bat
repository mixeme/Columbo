:: Run from project home with
:: .\scripts\build-win.bat

:: ----- Environment preparations -----
:: Install CPython interpreter from
::  https://www.python.org/downloads/windows/
:: Install pip
:: 	py -m ensurepip --upgrade
:: Upgrade pip
::  py -m pip install --upgrade pip
:: Install PyInstaller
:: 	py -m pip install --upgrade pyinstaller
:: ------------------------------------

:: Switch off output for each command
@echo off

:: Determine location of script
SET SCRIPT=%~dp0
echo Script's location: %SCRIPT%

:: Go to project home
cd %SCRIPT%
cd ..
echo Switch to project home: %cd%

SET BIN_NAME=columbo-win

:: Run PyInstaller
python -m PyInstaller ^
    --name %BIN_NAME% ^
	--onefile ^
 	--windowed ^
 	--noconfirm ^
	--clean ^
	--add-data="./src/gui;./src/gui" ^
	--add-data="./resources/icons;./resources/icons" ^
	--icon=resources/icons/search.ico ^
	src/main.py

rmdir /S /Q build
del %BIN_NAME%.spec

exit 0
