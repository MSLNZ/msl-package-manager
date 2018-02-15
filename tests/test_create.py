import os
import pytest
import shutil
import tempfile

import msl.package_manager as pm


def test_create():
    filename = 'akjdSKmkmklmKMgvrd4ESExKOKuh'
    pm.create(names=filename, author='Joe', email='a.b@c.com', path=tempfile.gettempdir())
    path = os.path.join(tempfile.gettempdir(), 'msl-'+filename)
    assert os.path.isdir(path)
    shutil.rmtree(path)

    with pytest.raises(TypeError):
        pm.create(names=filename, author=1)

    with pytest.raises(TypeError):
        pm.create(names=filename, author='joe', email=['joe'])
