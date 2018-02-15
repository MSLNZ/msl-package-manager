import msl.package_manager as pm


def test_pypi():
    pkgs = pm.helper.pypi()
    assert pm.PKG_NAME in pkgs
