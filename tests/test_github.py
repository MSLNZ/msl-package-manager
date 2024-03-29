import msl.package_manager as pm


def test_github():
    pkgs = pm.github()
    assert pm.utils._PKG_NAME in pkgs
    pkg = pkgs[pm.utils._PKG_NAME]
    assert len(pkg['description']) > 0
    assert len(pkg['version']) > 0
    assert len(pkg['tags']) > 10
    assert len(pkg['branches']) > 0
