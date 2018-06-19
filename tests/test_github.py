import msl.package_manager as pm


def test_github():
    pkgs = pm.github()
    assert pm.PKG_NAME in pkgs
