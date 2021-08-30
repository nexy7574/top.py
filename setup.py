from setuptools import setup
from re import compile

version_regex = compile(r"__version__ = \"(?P<v>[0-9]\.[0-9]{1,2}\.[0-9]+)(-(pre|alpha|beta)\.[0-9]+)?\"")

with open("./requirements.txt", encoding="utf-8") as requirements:
    reqs = requirements.read().splitlines()

with open("./README.md", encoding="utf-8") as readme_file:
    readme = readme_file.read()

with open("./toppy/client.py", encoding="utf-8") as client:
    ct = client.read()
    version = version_regex.search(ct).group("v")
    assert version is not None

setup(
    name="top.py",
    version=version,
    packages=["toppy", "toppy.models", "toppy.errors", "toppy.ratelimiter"],
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
        "ratelimit-persistence": ["aiosqlite"]
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
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Development Status :: 5 - Production/Stable",
    ],
)
