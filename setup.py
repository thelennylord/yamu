from setuptools import setup

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="yamu",
    version="0.1.0",
    py_modules=["yamu"],
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "yamu = yamu:main"
        ]
    }
)