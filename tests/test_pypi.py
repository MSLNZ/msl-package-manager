import msl.package_manager as pm


def test_pypi():
    pkgs = pm.pypi(update_cache=True)
    assert len(pkgs) == 5
    assert pm._PKG_NAME in pkgs
    assert 'msl-loadlib' in pkgs
    assert 'msl-network' in pkgs
    assert 'GTC' in pkgs
    assert 'Quantity-Value' in pkgs
