from setuptools import setup, find_packages

from crypto_fetch.constants import CF_NAME
from crypto_fetch.constants import CF_VERSION

setup(
   name=CF_NAME,
   version=CF_VERSION,
   description='Cli tool for fetching the latest cryptocurrency price data',
   author='rossliam2212',
   packages=find_packages(), 
   install_requires=[
       'requests>=2.32.5', 
       'colorama>=0.4.6',
       'pyyaml>=6.0.3'
    ],
    entry_points={
        "console_scripts": [
            "crypto-fetch=crypto_fetch.command_parser:main",
        ],
    }
)