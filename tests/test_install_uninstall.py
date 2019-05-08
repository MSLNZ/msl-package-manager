from msl.package_manager import utils, install, uninstall


def test_install_then_uninstall():

    # use MSL-LoadLib since it has no required dependencies to also install

    # make sure that MSL-LoadLib is not installed
    pkgs = utils.installed()
    if 'msl-loadlib' in pkgs:
        uninstall('loadlib', yes=True)
    pkgs = utils.installed()
    assert 'msl-loadlib' not in pkgs

    # install MSL-LoadLib
    install('loadlib', yes=True)

    # make sure that MSL-LoadLib is installed
    pkgs = utils.installed()
    assert 'msl-loadlib' in pkgs

    uninstall('loadlib', yes=True)

    # make sure that MSL-LoadLib is not installed
    pkgs = utils.installed()
    assert 'msl-loadlib' not in pkgs
