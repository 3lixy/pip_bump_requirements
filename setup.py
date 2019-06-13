import io
import sys

from setuptools import setup, find_packages

with io.open('README.rst', encoding='utf-8') as readme:
    long_description = readme.read()

# Populates __version__ without importing the package
__version__ = None
with io.open('pip_bump_requirements/_version.py', encoding='utf-8')as ver_file:
    exec (ver_file.read())  # pylint: disable=W0122
if not __version__:
    print('Could not find __version__ from pip_bump_requirements/_version.py')
    sys.exit(1)


def load_requirements(filename):
    with io.open(filename, encoding='utf-8') as reqfile:
        return [line.strip() for line in reqfile if not line.startswith('#')]


setup(
    name='pbr',
    version=__version__,
    description='Application to bump the versions in requirements.in',
    long_description=long_description,
    author='https://github.com/3lixy',
    # author_email='',
    license='MIT',
    url='',
    packages=find_packages(),
    # package_data={}
    include_package_data=True,
    # data_files=[],
    zip_safe=False,
    install_requires=load_requirements('requirements.txt'),
    # tests_require=['pytest'],
    # extras_require={},
    entry_points={
        'console_scripts': ['pbr = pip_bump_requirements:main'],
    },
    classifiers=[
        "Development Status :: 4 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7"
    ]
)
