import msl.package_manager as pm


def test_github():
    # if you send too many GET requests to the GitHub server your request
    # may be rejected which might also cause this test to fail
    pkgs = pm.github()
    assert pm.PKG_NAME in pkgs
