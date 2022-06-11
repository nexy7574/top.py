from os import chdir
from pathlib import Path
from re import compile
from warnings import warn

from setuptools import find_packages
from setuptools import setup

warn(DeprecationWarning("The setup.py install for this project is deprecated."))

chdir(Path(__file__).parent)

version_regex = compile(r"__version__ = \"(?P<v>\d\.\d{1,2}\.\d+)((a|b|(r)?c)\d+)?\"")

reqs = []

with open("./README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open("./toppy/client.py", encoding="utf-8") as client:
    ct = client.read()
    version = version_regex.search(ct).group("v")
    assert version is not None

setup(
    name="top.gg.py",
    version=version,
    packages=find_packages("tests"),
    url="https://github.com/dragdev-studios/top.py",
    license="MIT",
    author="EEKIM10",
    author_email="eek@clicksminuteper.net",
    description="A new, modern API wrapper for top.gg",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=reqs,
    extras_require={
        "tests": ["pytest", "flask", "requests"],
        "docs": ["sphinx", "sphinx-rtd-dark-mode"],
        "dev": ["pytest", "build", "black", "pycodestyle", "twine"]
    },
    python_requires=">=3.6",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Development Status :: 5 - Production/Stable",
    ],
)
