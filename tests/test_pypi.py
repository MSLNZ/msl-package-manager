import msl.package_manager as pm


def test_pypi():
    pkgs = pm.pypi()
    assert len(pkgs) == 3
    assert pm._PKG_NAME in pkgs
    assert 'msl-loadlib' in pkgs
    assert 'msl-network' in pkgs
