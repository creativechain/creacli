#!/usr/bin/env python

from setuptools import setup
import sys

assert sys.version_info[0] == 3, "creacli requires Python > 3"

__VERSION__ = '0.1.1'

setup(
    name='creacli',
    version=__VERSION__,
    description='Command line tool to interface with the Crea network',
    long_description=open('README.md').read(),
    download_url='https://github.com/creativechain/creacli/tarball/' + __VERSION__,
    author='Creativechain Foundation',
    author_email='info@creativechain.org',
    maintainer='Creativechain Foundation',
    maintainer_email='info@creativechain.org',
    url='http://library.creas.io/creacli',
    keywords=['crea', 'library', 'api', 'rpc', 'cli'],
    packages=["creacli"],
    # https://github.com/pallets/flask/issues/1562
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    entry_points={
        'console_scripts': [
            'creapy = creacli.__main__:main',
        ],
    },
    install_requires=[
        "crea-lib>=0.1.2",
        "prettytable==0.7.2",
        "colorama==0.3.6",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
)
