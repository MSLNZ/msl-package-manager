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
    assert os.path.isfile(os.path.join(root_dir, '.gitignore'))
    assert os.path.isfile(os.path.join(root_dir, 'CHANGES.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'condatests.py'))
    assert os.path.isfile(os.path.join(root_dir, 'LICENSE.txt'))
    assert os.path.isfile(os.path.join(root_dir, 'MANIFEST.in'))

    with open(os.path.join(root_dir, 'msl', '__init__.py'), 'r') as fp:
        lines = fp.read()
        assert 'DO NOT EDIT THIS FILE' in lines
        assert "__path__ = __import__('pkgutil').extend_path(__path__, __name__)" in lines

    with open(os.path.join(root_dir, 'msl', 'package', '__init__.py'), 'r') as fp:
        lines = fp.readlines()
        assert "__author__ = 'Measurement Standards Laboratory of New Zealand'\n" == lines[3]
        assert "__copyright__ = '\\xa9 {}, ' + __author__\n".format(datetime.now().strftime('%Y')) == lines[4]

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
        lines = fp.readlines()
        assert '    --cov msl\n' == lines[11]
        assert '    --ignore msl/examples\n' == lines[19]

    with open(os.path.join(root_dir, 'setup.py'), 'r') as fp:
        lines = fp.readlines()
        assert "'msl',  # the path to" in lines[33]
        assert "    init_text = read('msl/package/__init__.py')\n" == lines[90]
        assert "    name='msl-package',\n" == lines[150]
        assert "    url='https://github.com/MSLNZ/msl-package'" in lines[154]
        assert "    packages=find_packages(include=('msl*',)),\n" == lines[165]
        assert "import msl.package as p" in lines[175]
        assert "/msl/package/__init__.py" in lines[182]

    with open(os.path.join(root_dir, 'docs', 'conf.py'), 'r') as fp:
        lines = fp.readlines()
        assert 'from msl import package\n' == lines[10]
        assert "project = 'msl-package'\n" == lines[75]
        assert lines[76].startswith("copyright = package.__copyright__")
        assert 'author = package.__author__\n' == lines[77]
        assert 'version = package.__version__\n' == lines[84]
        assert 'release = package.__version__\n' == lines[86]
        assert 'msl-package.tex' in lines[160]

    with open(os.path.join(root_dir, 'docs', 'index.rst'), 'r') as fp:
        lines = fp.readlines()
        assert '.. _msl-package-welcome:\n' == lines[0]
        assert 'msl-package\n' == lines[2]
        assert '===========\n' == lines[3]

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
        assert os.path.isfile(os.path.join(root_dir, '.gitignore'))
        assert os.path.isfile(os.path.join(root_dir, 'CHANGES.rst'))
        assert os.path.isfile(os.path.join(root_dir, 'condatests.py'))
        assert os.path.isfile(os.path.join(root_dir, 'LICENSE.txt'))
        assert os.path.isfile(os.path.join(root_dir, 'MANIFEST.in'))

        with open(os.path.join(root_dir, 'pr', '__init__.py'), 'r') as fp:
            lines = fp.read()
            assert 'DO NOT EDIT THIS FILE' in lines
            assert "__path__ = __import__('pkgutil').extend_path(__path__, __name__)" in lines

        with open(os.path.join(root_dir, 'pr', 'Single_Photons', '__init__.py'), 'r') as fp:
            lines = fp.readlines()
            assert "__author__ = 'Measurement Standards Laboratory of New Zealand'\n" == lines[3]
            assert "__copyright__ = '\\xa9 {}, ' + __author__\n".format(datetime.now().strftime('%Y')) == lines[4]

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
            lines = fp.readlines()
            assert '    --cov pr\n' == lines[11]
            assert '    --ignore pr/examples\n' == lines[19]

        with open(os.path.join(root_dir, 'setup.py'), 'r') as fp:
            lines = fp.readlines()
            assert "'pr',  # the path to" in lines[33]
            assert "    init_text = read('pr/Single_Photons/__init__.py')\n" == lines[90]
            assert "    name='pr-Single-Photons',\n" == lines[150]
            assert "    url='https://github.com/MSLNZ/pr-Single-Photons'" in lines[154]
            assert "    packages=find_packages(include=('pr*',)),\n" == lines[165]
            assert "import pr.Single_Photons as p" in lines[175]
            assert "/pr/Single_Photons/__init__.py" in lines[182]

        with open(os.path.join(root_dir, 'docs', 'conf.py'), 'r') as fp:
            lines = fp.readlines()
            assert 'from pr import Single_Photons\n' == lines[10]
            assert "project = 'pr-Single-Photons'\n" == lines[75]
            assert lines[76].startswith("copyright = Single_Photons.__copyright__")
            assert 'author = Single_Photons.__author__\n' == lines[77]
            assert 'version = Single_Photons.__version__\n' == lines[84]
            assert 'release = Single_Photons.__version__\n' == lines[86]
            assert 'pr-Single-Photons.tex' in lines[160]

        with open(os.path.join(root_dir, 'docs', 'index.rst'), 'r') as fp:
            lines = fp.readlines()
            assert '.. _pr-Single-Photons-welcome:\n' == lines[0]
            assert 'pr-Single-Photons\n' == lines[2]
            assert '=================\n' == lines[3]

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
    assert os.path.isfile(os.path.join(root_dir, '.gitignore'))
    assert os.path.isfile(os.path.join(root_dir, 'CHANGES.rst'))
    assert os.path.isfile(os.path.join(root_dir, 'condatests.py'))
    assert os.path.isfile(os.path.join(root_dir, 'LICENSE.txt'))
    assert os.path.isfile(os.path.join(root_dir, 'MANIFEST.in'))

    with open(os.path.join(root_dir, 'time_tagger', '__init__.py'), 'r') as fp:
        lines = fp.readlines()
        assert "__author__ = 'Measurement Standards Laboratory of New Zealand'\n" == lines[3]
        assert "__copyright__ = '\\xa9 {}, ' + __author__\n".format(datetime.now().strftime('%Y')) == lines[4]

    with open(os.path.join(root_dir, '.coveragerc'), 'r') as fp:
        lines = fp.read()
        assert 'omit =' not in lines
        assert lines.endswith('title = time-tagger coverage report\n')

    with open(os.path.join(root_dir, 'AUTHORS.rst'), 'r') as fp:
        assert '* Time T. Tagger <time@tagger.com>' in fp.read()

    with open(os.path.join(root_dir, 'README.rst'), 'r') as fp:
        assert fp.read().startswith('time-tagger\n===========\n')

    with open(os.path.join(root_dir, 'setup.cfg'), 'r') as fp:
        lines = fp.readlines()
        assert '    --cov time_tagger\n' == lines[11]
        assert '    --ignore time_tagger/examples\n' != lines[19]

    with open(os.path.join(root_dir, 'setup.py'), 'r') as fp:
        lines = fp.readlines()
        assert "'time_tagger',  # the path to" in lines[33]
        assert "    init_text = read('time_tagger/__init__.py')\n" == lines[90]
        assert "    name='time-tagger',\n" == lines[150]
        assert "    url='https://github.com/MSLNZ/time-tagger'" in lines[154]
        assert "    packages=find_packages(include=('time_tagger',)),\n" == lines[165]
        assert "import time_tagger as p" in lines[175]
        assert "/time_tagger/__init__.py" in lines[182]

    with open(os.path.join(root_dir, 'docs', 'conf.py'), 'r') as fp:
        lines = fp.readlines()
        assert 'import time_tagger\n' == lines[10]
        assert "project = 'time-tagger'\n" == lines[75]
        assert lines[76].startswith("copyright = time_tagger.__copyright__")
        assert 'author = time_tagger.__author__\n' == lines[77]
        assert 'version = time_tagger.__version__\n' == lines[84]
        assert 'release = time_tagger.__version__\n' == lines[86]
        assert 'time-tagger.tex' in lines[160]

    with open(os.path.join(root_dir, 'docs', 'index.rst'), 'r') as fp:
        lines = fp.readlines()
        assert '.. _time-tagger-welcome:\n' == lines[0]
        assert 'time-tagger\n' == lines[2]
        assert '===========\n' == lines[3]

    shutil.rmtree(root_dir)
