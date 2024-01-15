SET mypath=%~dp0
echo %mypath:~0,-1%

for /F "delims=" %%i in (%filepath%) do set dirname="%%~dpi" 
echo %dirname%

python -m PyInstaller ^
	--clean ^
	--windowed ^
	--onefile ^
	--name columbo-win ^
	--add-data="./gui;./gui" ^
	--add-data="./icons;./icons" ^
	--icon=icons/search.ico ^
	main.py

::	--specpath ./build ^
