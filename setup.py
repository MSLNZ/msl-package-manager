import os
import re
import sys
from setuptools import setup, find_packages

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs'))
import docs_commands


def read(filename):
    with open(filename) as fp:
        text = fp.read()
    return text


def fetch_init(key):
    # open the __init__.py file to determine the value instead of importing the package to get the value
    init_text = read('msl/package_manager/__init__.py')
    return re.compile(r'{}\s+=\s+(.*)'.format(key)).search(init_text).group(1)[1:-1]


testing = {'test', 'tests', 'pytest'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if testing else []

needs_sphinx = {'doc', 'docs', 'apidoc', 'apidocs', 'build_sphinx'}.intersection(sys.argv)
sphinx = ['sphinx', 'sphinx_rtd_theme'] if needs_sphinx else []

setup(
    name=fetch_init('PKG_NAME'),
    author=fetch_init('__author__'),
    author_email='joseph.borbely@callaghaninnovation.govt.nz',
    url='https://github.com/MSLNZ/'+fetch_init('PKG_NAME'),
    version=fetch_init('__version__'),
    description='Install, uninstall, list and create MSL packages',
    long_description=read('README.rst'),
    platforms='any',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    setup_requires=sphinx + pytest_runner,
    tests_require=['pytest-cov', 'pytest', 'colorama'],
    install_requires=read('requirements.txt').split('\n'),
    cmdclass={
        'docs': docs_commands.BuildDocs,
        'apidocs': docs_commands.ApiDocs,
    },
    entry_points={
        'console_scripts': [
            'msl = msl.package_manager.cli:main',
        ],
    },
    packages=find_packages(include=('msl*',)) + ['template'],
    include_package_data=True,
    zip_safe=False,
)
