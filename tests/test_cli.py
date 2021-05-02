import logging

from msl.package_manager import utils, cli


def get_args(command):
    return cli.parse_args(command.split())


def test_install_update_args():

    for cmd in ('install', 'update', 'upgrade'):
        cmd += ' '

        args = get_args(cmd)
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag is None
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '-u')
        assert not args.names
        assert not args.all
        assert args.update_cache
        assert args.branch is None
        assert args.tag is None
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '--update-cache')
        assert not args.names
        assert not args.all
        assert args.update_cache
        assert args.branch is None
        assert args.tag is None
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '-b thebranch')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch == 'thebranch'
        assert args.tag is None
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '--branch thebranch --yes')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch == 'thebranch'
        assert args.tag is None
        assert args.quiet == 0
        assert args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '-t thetag')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag == 'thetag'
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '--tag thetag -qy')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag == 'thetag'
        assert args.quiet == 1
        assert args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '-t thetag --branch thebranch')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch == 'thebranch'
        assert args.tag == 'thetag'
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '-a')
        assert not args.names
        assert args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag is None
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '--all')
        assert not args.names
        assert args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag is None
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + 'package')
        assert len(args.names) == 1 and args.names[0] == 'package'
        assert not args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag is None
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '--all -t thetag --branch thebranch a bb cdfg package --update-cache')
        assert len(args.names) == 4
        assert args.names[0] == 'a'
        assert args.names[1] == 'bb'
        assert args.names[2] == 'cdfg'
        assert args.names[3] == 'package'
        assert args.all
        assert args.update_cache
        assert args.branch == 'thebranch'
        assert args.tag == 'thetag'
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '--log here.txt -t thetag --no-color --branch thebranch '
                              '--index-url https://my.index.org/simple --user')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch == 'thebranch'
        assert args.tag == 'thetag'
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 6
        assert args.pip_options[0] == '--log'
        assert args.pip_options[1] == 'here.txt'
        assert args.pip_options[2] == '--no-color'
        assert args.pip_options[3] == '--index-url'
        assert args.pip_options[4] == 'https://my.index.org/simple'
        assert args.pip_options[5] == '--user'

        args = get_args(cmd + 'io --log here.txt equipment -t thetag --no-color network '
                              '--branch thebranch -i https://my.index.org/simple --user loadlib')
        assert args.names == ['io', 'equipment', 'network', 'loadlib']
        assert not args.all
        assert not args.update_cache
        assert args.branch == 'thebranch'
        assert args.tag == 'thetag'
        assert args.quiet == 0
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 6
        assert args.pip_options[0] == '--log'
        assert args.pip_options[1] == 'here.txt'
        assert args.pip_options[2] == '--no-color'
        assert args.pip_options[3] == '-i'
        assert args.pip_options[4] == 'https://my.index.org/simple'
        assert args.pip_options[5] == '--user'

        args = get_args(cmd + 'io network --compile -qq --upgrade-strategy eager')
        assert args.names == ['io', 'network']
        assert not args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag is None
        assert args.quiet == 2
        assert not args.yes
        assert not args.disable_mslpm_version_check
        assert args.pip_options == ['--compile', '--upgrade-strategy', 'eager']

        args = get_args(cmd + '--no-deps -f file://home/ --all -y --retries 10')
        assert not args.names
        assert args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag is None
        assert args.quiet == 0
        assert args.yes
        assert not args.disable_mslpm_version_check
        assert args.pip_options == ['--no-deps', '-f', 'file://home/', '--retries', '10']


def test_uninstall_args():

    for cmd in ('uninstall', 'remove'):
        cmd += ' '

        args = get_args(cmd)
        assert not args.all
        assert not args.names
        assert not args.yes
        assert args.quiet == 0
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '-a')
        assert args.all
        assert not args.names
        assert not args.yes
        assert args.quiet == 0
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + '--all --yes')
        assert args.all
        assert not args.names
        assert args.yes
        assert args.quiet == 0
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 0

        args = get_args(cmd + 'package1 --log here.txt package2')
        assert not args.all
        assert args.names[0] == 'package1'
        assert args.names[1] == 'package2'
        assert args.quiet == 0
        assert not args.disable_mslpm_version_check
        assert not args.yes
        assert len(args.pip_options) == 2
        assert args.pip_options[0] == '--log'
        assert args.pip_options[1] == 'here.txt'

        args = get_args(cmd + '-a packageA -y')
        assert args.all
        assert args.names[0] == 'packageA'
        assert args.quiet == 0
        assert not args.disable_mslpm_version_check
        assert args.yes
        assert len(args.pip_options) == 0

        args = get_args(cmd + '--no-color -a packageA -y')
        assert args.all
        assert args.names[0] == 'packageA'
        assert args.yes
        assert args.quiet == 0
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 1
        assert args.pip_options[0] == '--no-color'

        args = get_args(cmd + 'qt -r reqs.txt io --no-color loadlib')
        assert not args.all
        assert args.names == ['qt', 'io', 'loadlib']
        assert not args.yes
        assert args.quiet == 0
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 3
        assert args.pip_options[0] == '-r'
        assert args.pip_options[1] == 'reqs.txt'
        assert args.pip_options[2] == '--no-color'


def test_list_args():

    args = get_args('list')
    assert not args.github
    assert not args.json
    assert not args.pypi
    assert not args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list -g')
    assert args.github
    assert not args.json
    assert not args.pypi
    assert not args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list --github')
    assert args.github
    assert not args.json
    assert not args.pypi
    assert not args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list --update-cache')
    assert not args.github
    assert not args.json
    assert not args.pypi
    assert args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list -u')
    assert not args.github
    assert not args.json
    assert not args.pypi
    assert args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list -j')
    assert not args.github
    assert args.json
    assert not args.pypi
    assert not args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list --json')
    assert not args.github
    assert args.json
    assert not args.pypi
    assert not args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list -j -g --update-cache')
    assert args.github
    assert args.json
    assert not args.pypi
    assert args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list -jgu')
    assert args.github
    assert args.json
    assert not args.pypi
    assert args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list -p --update-cache')
    assert not args.github
    assert not args.json
    assert args.pypi
    assert args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list --pypi --update-cache')
    assert not args.github
    assert not args.json
    assert args.pypi
    assert args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('list --invalid-pip-option --does-not-get-parsed-by-pip')
    assert not args.github
    assert not args.json
    assert not args.pypi
    assert not args.update_cache
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 2
    assert args.pip_options[0] == '--invalid-pip-option'
    assert args.pip_options[1] == '--does-not-get-parsed-by-pip'


def test_create_args():

    args = get_args('create')
    assert not args.names
    assert args.author is None
    assert args.email is None
    assert args.dir is None
    assert args.namespace is None
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('create -a first m. last -e my@email.com')
    assert not args.names
    assert len(args.author) == 3
    assert args.author[0] == 'first'
    assert args.author[1] == 'm.'
    assert args.author[2] == 'last'
    assert args.email == 'my@email.com'
    assert args.dir is None
    assert args.namespace is None
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('create --dir D:\\')
    assert not args.names
    assert args.author is None
    assert args.email is None
    assert args.dir == 'D:\\'
    assert args.namespace is None
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('create -a first m. last -e my@email.com --dir the/folder p1 pkg2 package3 d')
    assert len(args.names) == 4
    assert args.names[0] == 'p1'
    assert args.names[1] == 'pkg2'
    assert args.names[2] == 'package3'
    assert args.names[3] == 'd'
    assert len(args.author) == 3
    assert args.author[0] == 'first'
    assert args.author[1] == 'm.'
    assert args.author[2] == 'last'
    assert args.email == 'my@email.com'
    assert args.dir == 'the/folder'
    assert args.namespace is None
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('create --namespace pr')
    assert not args.names
    assert args.author is None
    assert args.email is None
    assert args.dir is None
    assert args.namespace == 'pr'
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('create -n pr')
    assert not args.names
    assert args.author is None
    assert args.email is None
    assert args.dir is None
    assert args.namespace == 'pr'
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 0

    args = get_args('create --invalid-pip-option XXX --does-not-get-parsed-by-pip')
    assert args.names == ['XXX']
    assert args.author is None
    assert args.email is None
    assert args.dir is None
    assert args.namespace is None
    assert args.quiet == 0
    assert not args.disable_mslpm_version_check
    assert len(args.pip_options) == 2
    assert args.pip_options[0] == '--invalid-pip-option'
    assert args.pip_options[1] == '--does-not-get-parsed-by-pip'


def test_quiet():

    args = get_args('list')
    assert args.quiet == 0
    assert utils.log.level == logging.DEBUG
    assert utils._pip_quiet == 0

    args = get_args('list --quiet')
    assert args.quiet == 1
    assert utils.log.level == logging.INFO
    assert utils._pip_quiet == 0

    args = get_args('list -q')
    assert args.quiet == 1
    assert utils.log.level == logging.INFO
    assert utils._pip_quiet == 0

    args = get_args('list --quiet --quiet')
    assert args.quiet == 2
    assert utils.log.level == logging.WARNING
    assert utils._pip_quiet == 1

    args = get_args('list -q -q')
    assert args.quiet == 2
    assert utils.log.level == logging.WARNING
    assert utils._pip_quiet == 1

    args = get_args('list -qq')
    assert args.quiet == 2
    assert utils.log.level == logging.WARNING
    assert utils._pip_quiet == 1

    args = get_args('list --quiet --quiet --quiet')
    assert args.quiet == 3
    assert utils.log.level == logging.ERROR
    assert utils._pip_quiet == 2

    args = get_args('list -q -q -q')
    assert args.quiet == 3
    assert utils.log.level == logging.ERROR
    assert utils._pip_quiet == 2

    args = get_args('list -qqq')
    assert args.quiet == 3
    assert utils.log.level == logging.ERROR
    assert utils._pip_quiet == 2

    args = get_args('list --quiet --quiet --quiet --quiet')
    assert args.quiet == 4
    assert utils.log.level > logging.CRITICAL
    assert utils._pip_quiet == 3

    args = get_args('list -q -q -q -q')
    assert args.quiet == 4
    assert utils.log.level > logging.CRITICAL
    assert utils._pip_quiet == 3

    args = get_args('list -qqqq')
    assert args.quiet == 4
    assert utils.log.level > logging.CRITICAL
    assert utils._pip_quiet == 3

    args = get_args('list --quiet --quiet --quiet --quiet --quiet')
    assert args.quiet == 5
    assert utils.log.level > logging.CRITICAL
    assert utils._pip_quiet == 3  # 3 is the maximum

    args = get_args('list -q -q -q -q -q')
    assert args.quiet == 5
    assert utils.log.level > logging.CRITICAL
    assert utils._pip_quiet == 3  # 3 is the maximum

    args = get_args('list -qqqqq')
    assert args.quiet == 5
    assert utils.log.level > logging.CRITICAL
    assert utils._pip_quiet == 3  # 3 is the maximum


def test_authorize():
    for command in ['authorise', 'authorize']:
        args = get_args(command + ' --invalid-pip-option notused --does-not-get-parsed-by-pip')
        assert args.quiet == 0
        assert not args.disable_mslpm_version_check
        assert len(args.pip_options) == 3
        assert args.pip_options[0] == '--invalid-pip-option'
        assert args.pip_options[1] == 'notused'
        assert args.pip_options[2] == '--does-not-get-parsed-by-pip'
