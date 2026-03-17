from setuptools import setup, find_packages # type: ignore

setup(
   name="crypto-fetch",
   version="1.0.0",
   description='Cli tool for fetching the latest cryptocurrency price data',
   author='rossliam2212',
   packages=find_packages(), 
   install_requires=[
       'requests>=2.32.5', 
       'colorama>=0.4.6',
       'pyyaml>=6.0.3',
       'rich>=13.0.0'
    ],
    entry_points={
        "console_scripts": [
            "crypto-fetch=crypto_fetch.command_parser:main",
        ],
    }
)