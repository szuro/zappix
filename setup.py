"""
Project home:
https://github.com/szuro/zappix
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='zappix',
    version='0.0.2',
    description='A Python replacement for Zabbix sender and get.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/szuro/zappix',
    author='Robert Szulist',
    author_email='r.szulist@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Monitoring',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='zabbix get sender',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['numpy'],
)