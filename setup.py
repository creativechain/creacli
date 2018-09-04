#!/usr/bin/env python

from setuptools import setup
import sys

assert sys.version_info[0] == 3, "dpaycli requires Python > 3"

__VERSION__ = '0.1.1'

setup(
    name='dpaycli',
    version=__VERSION__,
    description='Command line tool to interface with the dPay network',
    long_description=open('README.md').read(),
    download_url='https://github.com/dpays/dpaycli/tarball/' + __VERSION__,
    author='Jared Rice Sr.',
    author_email='<jared@benchx.io>',
    maintainer='Jared Rice Sr.',
    maintainer_email='<jared@benchx.io>',
    url='http://docs.dpays.io',
    keywords=['dpay', 'library', 'api', 'rpc', 'cli'],
    packages=["dpaycli"],
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
            'dpaypy = dpaycli.__main__:main',
        ],
    },
    install_requires=[
        "dpay-lib>=0.1.1",
        "prettytable==0.7.2",
        "colorama==0.3.6",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
)
