"""
PhishScope setup configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="phishscope",
    version="0.1.0",
    description="Evidence-Driven Phishing Analysis Agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="security@example.com",
    url="https://github.com/yourusername/PhishScope",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "playwright>=1.41.0",
    ],
    entry_points={
        "console_scripts": [
            "phishscope=phishscope:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP",
    ],
    keywords="phishing security analysis threat-intelligence forensics",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/PhishScope/issues",
        "Source": "https://github.com/yourusername/PhishScope",
    },
)

# Made with Bob
