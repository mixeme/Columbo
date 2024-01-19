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

:: Run PyInstaller
python -m PyInstaller ^
    --name columbo-win ^
	--onefile ^
 	--windowed ^
	--clean ^
	--add-data="./gui;./gui" ^
	--add-data="./icons;./icons" ^
	--icon=icons/search.ico ^
	main.py

exit 0
