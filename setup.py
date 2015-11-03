#!/usr/bin/env python3
from distutils.core import setup

from setuptools import find_packages

setup(
    name='Riley',
    version='1.0',
    description='Podcast aggregator',
    author='Daniel Jonsson',
    license='MIT',
    packages=find_packages(),
    entry_points={'console_scripts': ['riley = riley.main:main']},
)
