from setuptools import setup, find_packages

setup(
    name="rectangle-packing-framework",
    version="0.1.0",
    description="A modular framework for 2D rectangle packing problems",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "ortools>=9.0",
        "plotly>=5.0.0",
        "pytest>=7.0.0",
        "scipy>=1.7.0",
    ],
    python_requires=">=3.8",
)
