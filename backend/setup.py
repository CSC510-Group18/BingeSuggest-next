"""
Copyright (c) 2023 Aditya Pai, Ananya Mantravadi, Rishi Singhal, Samarth Shetty
This code is licensed under MIT license (see LICENSE for details)

@author: bingesuggest-next

Movie Recommender Setup Script

This script is used to package and distribute the Movie Recommender project.
It contains information about the project, including its name, version, authors,
description, and other relevant details, to facilitate distribution and installation.

For more information about the bingesuggest-next project, visit:
https://github.com/brwali/bingesuggest-next
"""

import setuptools

with open("README.md", "r", encoding="utf8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jrpowel9",  # Replace with your own username
    version="1.0.0",
    author="Robert, Brandon, Nicholas, Nathan",
    author_email="bingesuggest-next777@gmail.com",
    description="A movie recommendation engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/brwali/bingesuggest-next",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
