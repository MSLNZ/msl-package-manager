import os
import pytest
import shutil
import msl.package_manager as pm


def test_installed():
    pkgs = pm.get_installed()
    assert len(pkgs) > 0


def test_github():
    pkgs = pm.get_github()
    assert len(pkgs) > 0
    if 'None' not in pkgs:
        assert pm.NAME in pkgs


def test_invalid_command():
    with pytest.raises(ValueError):
        pm.main(command='whatever')


def test_create():
    filename = 'akjdSKmkmklmKMgvrd4ESExKOKuh'
    pm.main(command='create', names=[filename], author='Joe', email='a.b@c.com')
    assert os.path.isdir('msl-'+filename)
    shutil.rmtree('msl-'+filename)
