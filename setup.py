from setuptools import setup, find_packages

with open("README.MD", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="shf-format",
    version="0.9.0",
    author="Jackie Lin",
    author_email="linuxjackie@gmail.com",
    description="一個用於圍棋死活題的高效文本格式轉換工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/linuxjackie/shf_format",
    package_dir={"": "core"},  # 指定核心程式目錄
    packages=find_packages(where="core"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Board Games",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "sgf2shf=core.sgf2shf:main",
            "shf2sqlite=core.shf2sqlite:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
) 