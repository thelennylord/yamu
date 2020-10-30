from setuptools import setup

setup(
    name="yamu",
    version="0.1.0",
    py_modules=["yamu"],
    entry_points={
        "console_scripts": [
            "yamu = yamu:main"
        ]
    }
)