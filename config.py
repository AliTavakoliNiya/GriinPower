import os

# Base directory of the application
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory for data files
DATABASE_DIR = os.path.join(BASE_DIR, 'data')

# Database file path
DATABASE_DIR = os.path.join(DATABASE_DIR, 'GriinPower.db')
DATABASE_PATH = f'sqlite:///{DATABASE_DIR}'
print(DATABASE_PATH)

# Application settings
APP_NAME = "Electronic Component Manager"
APP_VERSION = "1.0.0"

COSNUS_PI = 0.85
ETA = 0.93
