from msl.package_manager import utils, install, uninstall


def test_install_then_uninstall():

    # make sure that MSL-LoadLib is NOT installed
    pkgs = utils.installed()
    assert 'msl-loadlib' not in pkgs

    # install from PyPI
    install('loadlib', yes=True)

    # make sure that MSL-LoadLib IS installed
    pkgs = utils.installed()
    assert 'msl-loadlib' in pkgs

    uninstall('loadlib', yes=True)

    # make sure that MSL-LoadLib is NOT installed
    pkgs = utils.installed()
    assert 'msl-loadlib' not in pkgs
