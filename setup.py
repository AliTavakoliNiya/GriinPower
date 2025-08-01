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
    "excludes": ["PyQt5.QtQml", "PyQt5.QtQuick"],  # <- QML disabled
    "include_files": [
        ("F:/Griin/GriinPower/assets", "assets")
    ]
}

base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable(
        "main.py",
        base=base,
        target_name="GriinPower.exe",
        icon="F:/Griin/GriinPower/assets/Logo.ico"
    )
]

setup(
    name="GriinPower",
    version="1.0",
    description="GriinPower Application",
    options={"build_exe": build_options},
    executables=executables
)
