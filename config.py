import os
import sys

# Base directory of the application
if getattr(sys, 'frozen', False):
    # If the app is run from a compiled executable
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # If the app is run as a .py script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database file path inside 'data' folder
DATABASE_FILE = os.path.join(BASE_DIR, 'data', 'GriinPower.db')
DATABASE_PATH = f'sqlite:///{DATABASE_FILE}'

# Application settings
APP_NAME = "Electronic Component Manager"
APP_VERSION = "1.0.0"

COSNUS_PI = 0.85
ETA = 0.93
