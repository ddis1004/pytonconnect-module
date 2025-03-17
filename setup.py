from setuptools import setup, find_packages

setup(
    name="pytonconnect_module",  
    version="0.1.0",
    packages=find_packages(include=["pytonconnect_module.*"]),
    install_requires=[  
        "pillow", 
        "qrcode"
    ],
    author="ddis1004",
    description="python tonconnect module, utilizing XaBbl4/pytonconnect",
    url="https://github.com/ddis1004/pytonconnect-module",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # 최소 Python 버전
)
