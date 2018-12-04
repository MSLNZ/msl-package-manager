import msl.package_manager as pm


def test_github():
    pkgs = pm.github(update_cache=True)
    assert pm._PKG_NAME in pkgs
    pkg = pkgs[pm._PKG_NAME]
    assert len(pkg['description']) > 0
    assert len(pkg['version']) > 0
    assert len(pkg['tags']) > 10
    assert len(pkg['branches']) > 0
