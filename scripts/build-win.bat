python -m PyInstaller ^
	--clean ^
	--windowed ^
	--onefile ^
	--name columbo-win ^
	--add-data="./gui;./gui" ^
	--add-data="./icons;./icons" ^
	--icon=icons/search.ico ^
	main.py