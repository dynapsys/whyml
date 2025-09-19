#!/usr/bin/env python3
"""
WhyML: Advanced YAML-based webpage generator with modular architecture
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements(filename):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, filename), encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]

setup(
    name="whyml",
    version="1.0.1",
    description="Advanced YAML-based webpage generator with modular architecture and multi-format conversion",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Tom Sapletta",
    author_email="info@softreck.dev",
    url="https://github.com/tom-sapletta-com/whyml",
    license="Apache-2.0",
    
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'docs']),
    package_data={
        'whyml': [
            'templates/*.yaml',
            'schemas/*.yaml',
            'static/*',
        ],
    },
    include_package_data=True,
    
    python_requires=">=3.8",
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'dev': read_requirements('requirements-dev.txt'),
        'server': ['fastapi>=0.100.0', 'uvicorn>=0.22.0'],
        'test': ['pytest>=7.0.0', 'pytest-cov>=4.0.0', 'pytest-asyncio>=0.21.0'],
    },
    
    entry_points={
        'console_scripts': [
            'whyml=whyml.cli:main',
            'whyml-server=whyml.server:main',
        ],
    },
    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    
    keywords=[
        "yaml", "manifest", "webpage-generator", "react", "vue", "php", "html",
        "converter", "modular", "web-scraper", "template-engine", "static-site"
    ],
    
    project_urls={
        "Documentation": "https://github.com/tom-sapletta-com/whyml/docs",
        "Source": "https://github.com/tom-sapletta-com/whyml",
        "Tracker": "https://github.com/tom-sapletta-com/whyml/issues",
    },
)
