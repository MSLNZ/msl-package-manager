import os
import pytest
import shutil
import tempfile

import msl.package_manager as pm


def test_create():
    filename = 'akjdskmkmklmkmgvrd4esexkokuh'
    pm.create(filename, author='Xyz', email='a.b@c.com', directory=tempfile.gettempdir())
    path = os.path.join(tempfile.gettempdir(), 'msl-'+filename)
    assert os.path.isdir(path)
    with open(os.path.join(path, 'AUTHORS.rst'), 'rt') as fp:
        lines = fp.read()
    assert '* Xyz <a.b@c.com>' in lines

    shutil.rmtree(path)

    with pytest.raises(TypeError):
        pm.create(filename, author=1)

    with pytest.raises(TypeError):
        pm.create(filename, author='joe', email=['joe'])
