#!/usr/bin/env python3
"""
Setup script for REAPER Language Interpreter

This script configures the Python package for the REAPER language interpreter,
including entry points, dependencies, and metadata.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "REAPER Language Interpreter - The Undead Programming Language"

# Read version from __init__.py
def read_version():
    init_path = os.path.join(os.path.dirname(__file__), 'interpreter', '__init__.py')
    if os.path.exists(init_path):
        with open(init_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    return "0.1.0"

setup(
    name="reaper-lang",
    version=read_version(),
    author="REAPER Language Team",
    author_email="reaper-lang@example.com",
    description="REAPER Language Interpreter - The Undead Programming Language",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/reaper-lang",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/reaper-lang/issues",
        "Source": "https://github.com/yourusername/reaper-lang",
        "Documentation": "https://github.com/yourusername/reaper-lang/blob/main/README.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies for core functionality
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "isort>=5.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
        "syntax": [
            "pygments>=2.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "reaper=interpreter.reaper:main",
        ],
    },
    include_package_data=True,
    package_data={
        "interpreter": [
            "test_examples/*.reaper",
            "examples/*.reaper",
            "*.md",
        ],
    },
    keywords=[
        "programming-language",
        "interpreter",
        "zombie",
        "death",
        "themed",
        "educational",
        "fun",
        "reaper",
        "undead",
    ],
    license="MIT",
    zip_safe=False,
    platforms=["any"],
    test_suite="tests",
    tests_require=["pytest>=6.0"],
)
