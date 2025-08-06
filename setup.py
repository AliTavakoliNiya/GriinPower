# python setup.py build

import sys
from cx_Freeze import setup, Executable

build_options = {
    "packages": [
        "bcrypt",
        "bs4",
        "numpy",
        "pandas",
        "PyQt5",
        "sqlalchemy"
    ],
    "excludes": ["PyQt5.QtQml", "PyQt5.QtQuick"],
    "include_files": [
        # Include the assets folder (will be copied to "assets/")
        ("D:/GriinPower/assets", "assets"),

        # Include the database file (copied into "data/GriinPower.db")
        ("D:/GriinPower/data/GriinPower.db", "data/GriinPower.db")
    ]
}

# Use Win32GUI base to hide the console for PyQt5 apps on Windows
base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable(
        "main.py",
        base=base,
        target_name="GriinPower.exe",
        icon="D:/GriinPower/assets/Logo.ico"
    )
]

setup(
    name="GriinPower",
    version="1.0",
    description="GriinPower Application",
    options={"build_exe": build_options},
    executables=executables
)
