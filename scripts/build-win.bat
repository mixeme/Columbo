:: Run from project home with
:: .\scripts\build-win.bat

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
	--clean ^
	--name columbo-win ^
	--add-data="./gui;./gui" ^
	--add-data="./icons;./icons" ^
	--icon=icons/search.ico ^
	main.py

:: 	--windowed ^
::	--onefile ^

exit 0
