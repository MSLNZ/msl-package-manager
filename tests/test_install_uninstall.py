from msl.package_manager import utils, install, uninstall


def test_install_then_uninstall():

    # make sure that MSL-IO is not installed
    pkgs = utils.installed()
    if 'msl-io' in pkgs:
        uninstall('io', yes=True)
    pkgs = utils.installed()
    assert 'msl-io' not in pkgs

    # install MSL-IO
    install('io', yes=True)

    # make sure that MSL-IO is installed
    pkgs = utils.installed()
    assert 'msl-io' in pkgs

    uninstall('io', yes=True)

    # make sure that MSL-IO is not installed
    pkgs = utils.installed()
    assert 'msl-io' not in pkgs
