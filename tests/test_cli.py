from msl.package_manager import cli, utils


def get_args(command):
    parser = cli.configure_parser()
    return parser.parse_args(command.split())


def test_install_update_args():

    for cmd in ('install', 'update', 'upgrade'):
        cmd += ' '

        args = get_args(cmd)
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag is None

        args = get_args(cmd + '-b thebranch')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch == 'thebranch'
        assert args.tag is None

        args = get_args(cmd + '--branch thebranch')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch == 'thebranch'
        assert args.tag is None

        args = get_args(cmd + '-t thetag')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag == 'thetag'

        args = get_args(cmd + '--tag thetag')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag == 'thetag'

        args = get_args(cmd + '-t thetag --branch thebranch')
        assert not args.names
        assert not args.all
        assert not args.update_cache
        assert args.branch == 'thebranch'
        assert args.tag == 'thetag'

        args = get_args(cmd + '-a')
        assert not args.names
        assert args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag is None

        args = get_args(cmd + '--all')
        assert not args.names
        assert args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag is None

        args = get_args(cmd + 'package')
        assert len(args.names) == 1 and args.names[0] == 'package'
        assert not args.all
        assert not args.update_cache
        assert args.branch is None
        assert args.tag is None

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


def test_uninstall_args():

    for cmd in ('uninstall', 'remove'):
        cmd += ' '

        args = get_args(cmd)
        assert not args.all
        assert not args.names

        args = get_args(cmd + '-a')
        assert args.all
        assert not args.names

        args = get_args(cmd + '--all')
        assert args.all
        assert not args.names

        args = get_args(cmd + 'package1 package2')
        assert not args.all
        assert args.names[0] == 'package1'
        assert args.names[1] == 'package2'

        args = get_args(cmd + '-a packageA')
        assert args.all
        assert args.names[0] == 'packageA'


def test_list_args():

    args = get_args('list')
    assert not args.github
    assert not args.json
    assert not args.pypi
    assert not args.update_cache

    args = get_args('list -g')
    assert args.github
    assert not args.json
    assert not args.pypi
    assert not args.update_cache

    args = get_args('list --github')
    assert args.github
    assert not args.json
    assert not args.pypi
    assert not args.update_cache

    args = get_args('list -g')
    assert args.github
    assert not args.json
    assert not args.pypi
    assert not args.update_cache

    args = get_args('list --update-cache')
    assert not args.github
    assert not args.json
    assert not args.pypi
    assert args.update_cache

    args = get_args('list -j')
    assert not args.github
    assert args.json
    assert not args.pypi
    assert not args.update_cache

    args = get_args('list --json')
    assert not args.github
    assert args.json
    assert not args.pypi
    assert not args.update_cache

    args = get_args('list -j -g --update-cache')
    assert args.github
    assert args.json
    assert not args.pypi
    assert args.update_cache

    args = get_args('list -p --update-cache')
    assert not args.github
    assert not args.json
    assert args.pypi
    assert args.update_cache

    args = get_args('list --pypi --update-cache')
    assert not args.github
    assert not args.json
    assert args.pypi
    assert args.update_cache


def test_create_args():

    args = get_args('create')
    assert not args.names
    assert args.author is None
    assert args.email is None
    assert args.path is None

    args = get_args('create -a first m. last -e my@email.com')
    assert not args.names
    assert len(args.author) == 3
    assert args.author[0] == 'first'
    assert args.author[1] == 'm.'
    assert args.author[2] == 'last'
    assert args.email == 'my@email.com'
    assert args.path is None

    args = get_args('create --path D:\\')
    assert not args.names
    assert args.author is None
    assert args.email is None
    assert args.path == 'D:\\'

    args = get_args('create -a first m. last -e my@email.com --path the/folder p1 pkg2 package3 d')
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
    assert args.path == 'the/folder'


def test_quiet():

    args = get_args('list --quiet')
    assert args.quiet == 1

    args = get_args('list -q')
    assert args.quiet == 1

    args = get_args('list -q -q')
    assert args.quiet == 2

    args = get_args('list -q -q -q')
    assert args.quiet == 3

    cli._main(*('list', ))
    assert utils._NUM_QUIET == 0

    cli._main(*('list', '-q'))
    assert utils._NUM_QUIET == 1

    cli._main(*('list', '-q', '-q'))
    assert utils._NUM_QUIET == 2

    cli._main(*('list', '-q', '-q', '-q'))
    assert utils._NUM_QUIET == 3

    cli._main(*('list', '-q', '-q', '-q', '-q'))
    assert utils._NUM_QUIET == 3  # 3 is the maximum allowed
