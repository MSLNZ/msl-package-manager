import os
import pytest
import shutil
import msl.package_manager as pm


def test_github():
    pkgs = pm.github()
    if pkgs:
        assert pm.PKG_NAME in pkgs


def test_create():
    filename = 'akjdSKmkmklmKMgvrd4ESExKOKuh'
    pm.create(names=filename, author='Joe', email='a.b@c.com')
    assert os.path.isdir('msl-'+filename)
    shutil.rmtree('msl-'+filename)

    with pytest.raises(TypeError):
        pm.create(names=[1, 2])

    with pytest.raises(TypeError):
        pm.create(names=filename, author=1)

    with pytest.raises(TypeError):
        pm.create(names=filename, author='joe', email=['joe'])
