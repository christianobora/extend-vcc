from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="extend-vcc",
    version="0.1.0",
    author="Christian Obora",
    author_email="christianobora@uchicago.edu",
    description="Manage virtual cards on Extend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/christianobora/extend-vcc",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Communications :: Email",
    ],
    python_requires=">=3.8",
    install_requires=["requests>=2.26.0", "requests-toolbelt>=1.0.0",],
    extras_require={
        "dev": [
            "pytest>=8.3.4",
            "pytest-cov>=3.0.0",
            "mypy>=1.0.0",
            "black>=24.10.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
        ],
        "test": [
            "pytest>=8.3.4",
            "pytest-cov>=3.0.0",
        ],
        "all": [
            "aiohttp>=3.8.0",
            "pytest>=8.3.4",
            "pytest-cov>=3.0.0",
        ],
        "examples": [],
    },
    keywords="extend virtual card",
)
