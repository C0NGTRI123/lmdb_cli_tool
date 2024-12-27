import os
from typing import List
from setuptools import find_packages, setup


def get_requires() -> List[str]:
    default_requires = [
        "loguru>=0.7.0",
        "lmdb>=1.3.0", 
        "numpy>=1.21.0",
        "Pillow>=9.0.0",
        "tqdm>=4.65.0",
        "PyYAML>=6.0",
        "psutil>=5.9.0"
    ]
    
    try:
        with open("requirements.txt", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return default_requires


def get_console_scripts() -> List[str]:
    """
    Generate a list of console script entry points for CLI commands.
    """
    console_scripts = ["lmdb-cli = lmdb_cli_tool.cli:main"]  # Changed to list
    if os.environ.get("ENABLE_SHORT_CONSOLE", "1").lower() in ["true", "1"]:
        console_scripts.append("lmf = lmdb_cli_tool.cli:main")
    return console_scripts


setup(
    name="lmdb_cli_tool",
    version="0.0.0.dev0",
    author="congtri",
    author_email="congtri13052000@gmail.com",
    description="Write and read LMDB datasets",

    # Package discovery and dependencies
    install_requires=get_requires(),
    packages=find_packages(),
    # package_dir={"": "src"},
    # packages=find_packages(where="src"),
    python_requires=">=3.8",
    
    
    # Build and development requirements
    setup_requires=[
        "wheel",
        "setuptools",
        "build"
    ],

    # Entry points
    entry_points={"console_scripts": get_console_scripts()},

    # Package data and metadata
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],

    # Project URLs
    project_urls={
        "Source": "https://github.com/C0NGTRI123/lmdb_cli_tool",
        "Bug Reports": "https://github.com/C0NGTRI123/lmdb_cli_tool/issues",
    },
)
