import PyInstaller.__main__
import sys
import os
import shutil

# Make sure we clean up previous builds to avoid conflicts
for d in ['build', 'dist']:
    if os.path.exists(d):
        shutil.rmtree(d)

print("Building Transport Management System...")

args = [
    'main.py',
    '--name=TransportSystem',
    '--windowed', # No console window
    '--noconfirm', # Overwrite output directory without asking
    '--add-data=themes;themes',
    '--add-data=.env;.',
    '--add-data=theme_config.json;.',
    '--hidden-import=psycopg2',
    '--hidden-import=dotenv',
    '--hidden-import=PyQt6.QtWebEngineWidgets',
    '--hidden-import=folium',
    '--hidden-import=jinja2',
    '--hidden-import=branca'
]

# Check if assets exist and include them if so
if os.path.exists('assets'):
    args.append('--add-data=assets;assets')

PyInstaller.__main__.run(args)

print("Build completed successfully. Check the 'dist' folder for the executable.")
