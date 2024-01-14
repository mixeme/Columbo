# Prepare
cd D:\Sync\Документы\Творчество\Программирование\Python\Columbo

# Auto-py-to-exe
auto-py-to-exe

# PyInstaller  
python -m PyInstaller --onefile --windowed main.py

# Nuitka (doesn't work)
nuitka --standalone main.py

# Copy resources
cp gui dist\
cp icons dist\
