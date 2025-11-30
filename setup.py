"""
Setup script for Social Arena Recommendation System.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="social-arena-recommendation",
    version="1.0.0",
    description="Twitter-style recommendation system for Social Arena",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Social Arena Team",
    url="https://github.com/Social-Arena/Recommendation",
    packages=find_packages(exclude=["tests", "examples", "trace"]),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="recommendation-system, social-media, twitter, agent-simulation",
    project_urls={
        "Bug Reports": "https://github.com/Social-Arena/Recommendation/issues",
        "Source": "https://github.com/Social-Arena/Recommendation",
    },
)

