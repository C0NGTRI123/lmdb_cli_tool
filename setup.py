import os
from typing import List
from setuptools import find_packages, setup

def get_requires() -> List[str]:
    with open("requirements.txt", encoding="utf-8") as f:
        file_content = f.read()
        lines = [line.strip() for line in file_content.strip().split("\n") if not line.startswith("#")]
        return lines

def get_console_scripts() -> List[str]:
    """
    Generate a list of console script entry points for CLI commands.
    """
    console_scripts = ["lmdb-cli = cli:main"]  # Changed to list
    if os.environ.get("ENABLE_SHORT_CONSOLE", "1").lower() in ["true", "1"]:
        console_scripts.append("lmf = cli:main")
    return console_scripts

setup(
    name="llm_lmdb",
    version="0.0.0.dev0",
    description="Write and read LMDB datasets",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={"console_scripts": get_console_scripts()},
    include_package_data=True,
    install_requires=get_requires(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)