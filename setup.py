import sys
from setuptools import setup, find_packages
from msl import package_manager


def read(filename):
    with open(filename) as fp:
        text = fp.read()
    return text


testing = {'test', 'tests', 'pytest'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if testing else []

needs_sphinx = {'doc', 'docs', 'apidoc', 'apidocs', 'build_sphinx'}.intersection(sys.argv)
sphinx = ['sphinx', 'sphinx_rtd_theme'] if needs_sphinx else []


setup(
    name=package_manager.NAME,
    author=package_manager.__author__,
    author_email='joseph.borbely@callaghaninnovation.govt.nz',
    url='https://github.com/MSLNZ/msl-package-manager',
    version=package_manager.__version__,
    description='MSL Package Manager to install, uninstall, list and create MSL packages',
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
    tests_require=['pytest-cov', 'pytest'] if testing else [],
    namespace_packages=['msl'],
    packages=find_packages(include=('msl*',)) + ['template'],
    install_requires=read('requirements.txt').split(),
    entry_points={
        'console_scripts': [
            'msl = msl.package_manager.main:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
