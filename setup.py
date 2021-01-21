from setuptools import setup

with open("requirements.txt") as requirements:
    reqs = requirements.readlines()

with open("README.md") as readme_file:
    readme = readme_file.read()

setup(
    name='top.py',
    version='0.1.0',
    packages=['toppy', 'toppy.models'],
    url='https://github.com/dragdev-studios/top.py',
    license='MIT',
    author='EEKIM10',
    requirements=reqs,
    author_email='eek@clicksminuteper.net',
    description='A new, modern API wrapper for top.gg',
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "fullmap": ["requests"]
    },
    python_requires=">=3.6",
    classifiers=[
        'License :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
