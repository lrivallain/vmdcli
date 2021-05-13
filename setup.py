#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
import vmdcli

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    "click",
    "requests",
    "pytz",
    "humanize",
    "pushbullet.py"
]

setup_requirements = [ ]

test_requirements = [ ]

description = "Ce projet est un petit outil en ligne de commande, permettant de détecter les rendez-vous disponibles "
description += "dans votre département pour recevoir un vaccin contre la covid19."

setup(
    author="Ludovic Rivallain",
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description=description,
    long_description_content_type = "text/markdown",
    entry_points={
        'console_scripts': [
            'vmd-cli=vmdcli.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='vmdcli',
    name='vmdcli',
    packages=find_packages(include=['vmdcli', 'vmdcli.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/lrivallain/vmdcli',
    version=vmdcli.__version__,
    zip_safe=False,
)
