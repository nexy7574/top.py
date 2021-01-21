from setuptools import setup

with open("requirements.txt") as requirements:
    reqs = requirements.readlines()

setup(
    name='top.py',
    version='0.1.0',
    packages=['toppy', 'toppy.models'],
    url='https://github.com/dragdev-studios/top.py',
    license='MIT',
    author='EEKIM10',
    requirements=reqs,
    author_email='eek@clicksminuteper.net',
    description='A new, modern API wrapper for top.gg'
)
