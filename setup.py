import io
import os
from setuptools import setup, find_packages

version = io.open('rubyenv/_version.py').readlines()[-1].split()[-1].strip('"\'')

setup(
    name='rubyenv',
    version=version,

    description='manage ruby in your virtualenv',
    long_description=io.open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Tommy Wang',
    author_email='twang@august8.net',
    url='http://github.com/twang817/rubyenv',
    download_url='https://github.com/twang817/rubyenv/tarball/{version}'.format(version=version),

    packages=find_packages(),
    install_requires=['gitpython', 'six', 'future'],
    include_package_data=True,

    entry_points={
        'console_scripts': ['rubyenv = rubyenv:main'],
    },

    license='MIT',
    platforms=['any'],
    keywords='ruby virtualenv',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],
)
