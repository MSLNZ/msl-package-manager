import msl.package_manager as pm


def test_pypi():
    pkgs = pm.pypi()
    assert pm.PKG_NAME in pkgs
