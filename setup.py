import sys
from setuptools import setup, find_packages
from distutils.cmd import Command


testing = {'test', 'tests', 'pytest'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if testing else []

needs_sphinx = {'doc', 'docs', 'apidoc', 'apidocs', 'build_sphinx'}.intersection(sys.argv)
sphinx = ['sphinx', 'sphinx_rtd_theme'] if needs_sphinx else []

if not testing:
    from msl import package_manager
    name = package_manager.PKG_NAME
    author = package_manager.__author__
    version = package_manager.__version__
else:
    name = author = version = 'test'


class ApiDocs(Command):
    """
    A custom command that calls sphinx-apidoc
    see: http://www.sphinx-doc.org/en/latest/man/sphinx-apidoc.html
    """
    description = "builds the api documentation using sphinx-apidoc"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sphinx.apidoc import main
        main([
            'sphinx-apidoc',
            '--force',  # Overwrite existing files
            '--module-first',  # Put module documentation before submodule documentation
            '--separate',  # Put documentation for each module on its own page
            '-o', './docs/_autosummary',
            'msl',
        ])
        sys.exit(0)


class BuildDocs(Command):
    """
    A custom command that calls sphinx-build
    see: http://www.sphinx-doc.org/en/latest/man/sphinx-build.html
    """
    description = "builds the documentation using sphinx-build"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from sphinx import build_main
        build_main([
            'sphinx-build',
            '-b', 'html',  # builder to use
            '-a',  # generate output for all files
            '-E',  # ignore cached files, forces to re-read all source files from disk
            'docs',  # source directory
            './docs/_build/html', # output directory
        ])
        sys.exit(0)


def read(filename):
    with open(filename) as fp:
        text = fp.read()
    return text


setup(
    name=name,
    author=author,
    author_email='joseph.borbely@callaghaninnovation.govt.nz',
    url='https://github.com/MSLNZ/msl-package-manager',
    version=version,
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
    tests_require=['pytest-cov', 'pytest', 'colorama'],
    install_requires=read('requirements.txt').split(),
    cmdclass={'docs': BuildDocs, 'apidocs': ApiDocs},
    namespace_packages=['msl'],
    packages=find_packages(include=('msl*',)) + ['template'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'msl = msl.package_manager.cli:main',
        ],
    },
    zip_safe=False,
)
