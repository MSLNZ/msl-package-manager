import os
import shutil
import tempfile
from datetime import datetime

import pytest

import msl.package_manager as pm

temp_dir = tempfile.gettempdir()


def test_invalid_kwarg_types():
    with pytest.raises(TypeError):
        pm.create('abc', author=1)

    with pytest.raises(TypeError):
        pm.create('abc', author='a', email=['a'])


def test_create_msl_package():
    root_dir = os.path.join(temp_dir, 'msl-package')
    if os.path.isdir(root_dir):
        shutil.rmtree(root_dir)

    pm.create('package', author='Abc Def', email='a.b@c.com', directory=temp_dir)

    assert os.path.isdir(root_dir)
    assert os.path.isdir(os.path.join(root_dir, 'msl'))
    assert os.path.isdir(os.path.join(root_dir, 'msl', 'package'))
    assert os.path.isdir(os.path.join(root_dir, 'msl', 'examples'))
    assert os.path.isdir(os.path.join(root_dir, 'msl', 'examples', 'package'))
    assert os.path.isdir(os.path.join(root_dir, 'docs'))
    assert os.path.isdir(os.path.join(root_dir, 'docs', '_static'))
    assert os.path.isdir(os.path.join(root_dir, 'tests'))
    assert os.path.isfile(os.path.join(root_dir, '.coveragerc'))
    assert os.path.isfile(os.path.join(root_dir, '.gitignore'))
    assert os.path.isfile(os.path.join(root_dir, 'AUTHORS.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'CHANGES.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'condatests.py'))
    assert os.path.isfile(os.path.join(root_dir, 'LICENSE.txt'))
    assert os.path.isfile(os.path.join(root_dir, 'MANIFEST.in'))
    assert os.path.isfile(os.path.join(root_dir, 'README.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'setup.cfg'))
    assert os.path.isfile(os.path.join(root_dir, 'setup.py'))
    assert os.path.isfile(os.path.join(root_dir, 'docs', 'authors.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'docs', 'changelog.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'docs', 'conf.py'))
    assert os.path.isfile(os.path.join(root_dir, 'docs', 'index.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'docs', 'license.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'tests', 'README'))

    with open(os.path.join(root_dir, 'msl', '__init__.py'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert 'DO NOT EDIT THIS FILE.' == lines[1]
        assert lines[3].endswith('**msl** namespace.')
        assert "__path__ = __import__('pkgutil').extend_path(__path__, __name__)" == lines[5]

    with open(os.path.join(root_dir, 'msl', 'package', '__init__.py'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert "__author__ = 'Measurement Standards Laboratory of New Zealand'" == lines[3]
        assert "__copyright__ = '\\xa9 {}, ' + __author__".format(datetime.now().strftime('%Y')) == lines[4]

    with open(os.path.join(root_dir, 'msl', 'examples', '__init__.py'), 'r') as fp:
        assert '# DO NOT EDIT THIS FILE.\n' == fp.read()

    with open(os.path.join(root_dir, 'msl', 'examples', 'package', '__init__.py'), 'r') as fp:
        assert '' == fp.read()

    with open(os.path.join(root_dir, '.coveragerc'), 'r') as fp:
        lines = fp.read()
        assert 'omit =\n    msl/examples/*' in lines
        assert lines.endswith('title = msl-package coverage report\n')

    with open(os.path.join(root_dir, 'AUTHORS.rst'), 'r') as fp:
        assert '* Abc Def <a.b@c.com>' in fp.read()

    with open(os.path.join(root_dir, 'README.rst'), 'r') as fp:
        assert fp.read().startswith('msl-package\n===========\n')

    with open(os.path.join(root_dir, 'setup.cfg'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert '    --cov msl' == lines[11]
        assert '    --ignore msl/examples' == lines[19]

    with open(os.path.join(root_dir, 'setup.py'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert "'msl',  # the path to" in lines[32]
        assert "# specify the packages that msl-package depends on" == lines[147]
        assert "init_original = 'msl/package/__init__.py'" == lines[162]
        assert "    name='msl-package'," == lines[167]
        assert "    url='https://github.com/MSLNZ/msl-package'," == lines[171]
        assert "    description='Write a short description about msl-package here'," == lines[172]
        assert "    packages=find_packages(include=('msl*',))," == lines[182]

    with open(os.path.join(root_dir, 'docs', 'conf.py'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert 'from msl import package' == lines[10]
        assert "project = 'msl-package'" == lines[75]
        assert lines[76].startswith("copyright = package.__copyright__")
        assert 'author = package.__author__' == lines[77]
        assert 'version = package.__version__' == lines[84]
        assert 'release = package.__version__' == lines[86]
        assert 'msl-package.tex' in lines[160]

    with open(os.path.join(root_dir, 'docs', 'index.rst'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert '.. _msl-package-welcome:' == lines[0]
        assert 'msl-package' == lines[2]
        assert '===========' == lines[3]

    shutil.rmtree(root_dir)


def test_create_pr_single_photons():
    root_dir = os.path.join(temp_dir, 'pr-Single-Photons')
    if os.path.isdir(root_dir):
        shutil.rmtree(root_dir)

    for namespace in ['pr', 'pr-', 'PR----']:
        pm.create('Single-Photons', author='joe', email='joe@email.com', namespace=namespace, directory=temp_dir)

        assert os.path.isdir(root_dir)
        assert os.path.isdir(os.path.join(root_dir, 'pr'))
        assert os.path.isdir(os.path.join(root_dir, 'pr', 'Single_Photons'))
        assert os.path.isdir(os.path.join(root_dir, 'pr', 'examples'))
        assert os.path.isdir(os.path.join(root_dir, 'pr', 'examples', 'Single_Photons'))
        assert os.path.isdir(os.path.join(root_dir, 'docs'))
        assert os.path.isdir(os.path.join(root_dir, 'docs', '_static'))
        assert os.path.isdir(os.path.join(root_dir, 'tests'))
        assert os.path.isfile(os.path.join(root_dir, '.coveragerc'))
        assert os.path.isfile(os.path.join(root_dir, '.gitignore'))
        assert os.path.isfile(os.path.join(root_dir, 'AUTHORS.rst'))
        assert os.path.isfile(os.path.join(root_dir, 'CHANGES.rst'))
        assert os.path.isfile(os.path.join(root_dir, 'condatests.py'))
        assert os.path.isfile(os.path.join(root_dir, 'LICENSE.txt'))
        assert os.path.isfile(os.path.join(root_dir, 'MANIFEST.in'))
        assert os.path.isfile(os.path.join(root_dir, 'README.rst'))
        assert os.path.isfile(os.path.join(root_dir, 'setup.cfg'))
        assert os.path.isfile(os.path.join(root_dir, 'setup.py'))
        assert os.path.isfile(os.path.join(root_dir, 'docs', 'authors.rst'))
        assert os.path.isfile(os.path.join(root_dir, 'docs', 'changelog.rst'))
        assert os.path.isfile(os.path.join(root_dir, 'docs', 'conf.py'))
        assert os.path.isfile(os.path.join(root_dir, 'docs', 'index.rst'))
        assert os.path.isfile(os.path.join(root_dir, 'docs', 'license.rst'))
        assert os.path.isfile(os.path.join(root_dir, 'tests', 'README'))

        with open(os.path.join(root_dir, 'pr', '__init__.py'), 'r') as fp:
            lines = [line.rstrip() for line in fp.readlines()]
            assert 'DO NOT EDIT THIS FILE.' == lines[1]
            assert lines[3].endswith('**pr** namespace.')
            assert "__path__ = __import__('pkgutil').extend_path(__path__, __name__)" == lines[5]

        with open(os.path.join(root_dir, 'pr', 'Single_Photons', '__init__.py'), 'r') as fp:
            lines = [line.rstrip() for line in fp.readlines()]
            assert "__author__ = 'Measurement Standards Laboratory of New Zealand'" == lines[3]
            assert "__copyright__ = '\\xa9 {}, ' + __author__".format(datetime.now().strftime('%Y')) == lines[4]

        with open(os.path.join(root_dir, 'pr', 'examples', '__init__.py'), 'r') as fp:
            assert '# DO NOT EDIT THIS FILE.\n' == fp.read()

        with open(os.path.join(root_dir, 'pr', 'examples', 'Single_Photons', '__init__.py'), 'r') as fp:
            assert '' == fp.read()

        with open(os.path.join(root_dir, '.coveragerc'), 'r') as fp:
            lines = fp.read()
            assert 'omit =\n    pr/examples/*' in lines
            assert lines.endswith('title = pr-Single-Photons coverage report\n')

        with open(os.path.join(root_dir, 'AUTHORS.rst'), 'r') as fp:
            assert '* joe <joe@email.com>' in fp.read()

        with open(os.path.join(root_dir, 'README.rst'), 'r') as fp:
            assert fp.read().startswith('pr-Single-Photons\n=================\n')

        with open(os.path.join(root_dir, 'setup.cfg'), 'r') as fp:
            lines = [line.rstrip() for line in fp.readlines()]
            assert '    --cov pr' == lines[11]
            assert '    --ignore pr/examples' == lines[19]

        with open(os.path.join(root_dir, 'setup.py'), 'r') as fp:
            lines = [line.rstrip() for line in fp.readlines()]
            assert "'pr',  # the path to" in lines[32]
            assert "# specify the packages that pr-Single-Photons depends on" == lines[147]
            assert "init_original = 'pr/Single_Photons/__init__.py'" == lines[162]
            assert "    name='pr-Single-Photons'," == lines[167]
            assert "    url='https://github.com/MSLNZ/pr-Single-Photons'," == lines[171]
            assert "    description='Write a short description about pr-Single-Photons here'," == lines[172]
            assert "    packages=find_packages(include=('pr*',))," == lines[182]

        with open(os.path.join(root_dir, 'docs', 'conf.py'), 'r') as fp:
            lines = [line.rstrip() for line in fp.readlines()]
            assert 'from pr import Single_Photons' == lines[10]
            assert "project = 'pr-Single-Photons'" == lines[75]
            assert lines[76].startswith("copyright = Single_Photons.__copyright__")
            assert 'author = Single_Photons.__author__' == lines[77]
            assert 'version = Single_Photons.__version__' == lines[84]
            assert 'release = Single_Photons.__version__' == lines[86]
            assert 'pr-Single-Photons.tex' in lines[160]

        with open(os.path.join(root_dir, 'docs', 'index.rst'), 'r') as fp:
            lines = [line.rstrip() for line in fp.readlines()]
            assert '.. _pr-Single-Photons-welcome:' == lines[0]
            assert 'pr-Single-Photons' == lines[2]
            assert '=================' == lines[3]

        shutil.rmtree(root_dir)


def test_create_no_namespace():
    root_dir = os.path.join(temp_dir, 'time-tagger')
    if os.path.isdir(root_dir):
        shutil.rmtree(root_dir)

    pm.create('time-tagger', author=['Time', 'T.', 'Tagger'],
              email='time@tagger.com', directory=temp_dir, namespace=None)

    assert os.path.isdir(root_dir)
    assert os.path.isdir(os.path.join(root_dir, 'time_tagger'))
    assert os.path.isdir(os.path.join(root_dir, 'docs'))
    assert os.path.isdir(os.path.join(root_dir, 'docs', '_static'))
    assert os.path.isdir(os.path.join(root_dir, 'tests'))
    assert os.path.isfile(os.path.join(root_dir, '.coveragerc'))
    assert os.path.isfile(os.path.join(root_dir, '.gitignore'))
    assert os.path.isfile(os.path.join(root_dir, 'AUTHORS.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'CHANGES.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'condatests.py'))
    assert os.path.isfile(os.path.join(root_dir, 'LICENSE.txt'))
    assert os.path.isfile(os.path.join(root_dir, 'MANIFEST.in'))
    assert os.path.isfile(os.path.join(root_dir, 'README.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'setup.cfg'))
    assert os.path.isfile(os.path.join(root_dir, 'setup.py'))
    assert os.path.isfile(os.path.join(root_dir, 'docs', 'authors.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'docs', 'changelog.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'docs', 'conf.py'))
    assert os.path.isfile(os.path.join(root_dir, 'docs', 'index.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'docs', 'license.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'tests', 'README'))

    with open(os.path.join(root_dir, 'time_tagger', '__init__.py'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert "__author__ = 'Measurement Standards Laboratory of New Zealand'" == lines[3]
        assert "__copyright__ = '\\xa9 {}, ' + __author__".format(datetime.now().strftime('%Y')) == lines[4]

    with open(os.path.join(root_dir, '.coveragerc'), 'r') as fp:
        lines = fp.read()
        assert 'omit =' not in lines
        assert lines.endswith('title = time-tagger coverage report\n')

    with open(os.path.join(root_dir, 'AUTHORS.rst'), 'r') as fp:
        assert '* Time T. Tagger <time@tagger.com>' in fp.read()

    with open(os.path.join(root_dir, 'README.rst'), 'r') as fp:
        assert fp.read().startswith('time-tagger\n===========\n')

    with open(os.path.join(root_dir, 'setup.cfg'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert '    --cov time_tagger' == lines[11]
        assert '    --ignore time_tagger/examples' != lines[19]

    with open(os.path.join(root_dir, 'setup.py'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert "'time_tagger',  # the path to" in lines[32]
        assert "# specify the packages that time-tagger depends on" == lines[147]
        assert "init_original = 'time_tagger/__init__.py'" == lines[162]
        assert "    name='time-tagger'," == lines[167]
        assert "    url='https://github.com/MSLNZ/time-tagger'," == lines[171]
        assert "    description='Write a short description about time-tagger here'," == lines[172]
        assert "    packages=find_packages(include=('time_tagger',))," == lines[182]

    with open(os.path.join(root_dir, 'docs', 'conf.py'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert 'import time_tagger' == lines[10]
        assert "project = 'time-tagger'" == lines[75]
        assert lines[76].startswith("copyright = time_tagger.__copyright__")
        assert 'author = time_tagger.__author__' == lines[77]
        assert 'version = time_tagger.__version__' == lines[84]
        assert 'release = time_tagger.__version__' == lines[86]
        assert 'time-tagger.tex' in lines[160]

    with open(os.path.join(root_dir, 'docs', 'index.rst'), 'r') as fp:
        lines = [line.rstrip() for line in fp.readlines()]
        assert '.. _time-tagger-welcome:' == lines[0]
        assert 'time-tagger' == lines[2]
        assert '===========' == lines[3]

    shutil.rmtree(root_dir)
