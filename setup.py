from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('', ['conferences.py', 'config_manager.py', 'apple_integration.py', 'widget.py', 'ui_main.py']),
]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PyQt6'],
    'plist': {
        'CFBundleName': 'Deadline Tracker',
        'CFBundleDisplayName': 'Deadline Tracker',
        'CFBundleIdentifier': 'com.jialonglong.deadlinetracker',
        'CFBundleVersion': '1.1.0',
        'CFBundleShortVersionString': '1.1.0',
        'LSMinimumSystemVersion': '10.15',
        'NSHighResolutionCapable': True,
        'LSUIElement': False,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
