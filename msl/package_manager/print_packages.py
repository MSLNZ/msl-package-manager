"""
Print the list of MSL packages that are installed or that can be installed.
"""
from .helper import pypi
from .helper import github
from .helper import installed


def print_packages(from_github=False, detailed=False, from_pypi=False, update_cache=False):
    """Print the list of MSL packages that are available.

    The list of packages can be either those that are installed, those that are
    available as repositories_ on GitHub or packages available on PyPI_.

    .. _repositories: https://github.com/MSLNZ
    .. _packages: https://pypi.org/search/?q=msl-*
    .. _PyPI: https://pypi.org/search/?q=msl-*
    
    Parameters
    ----------
    from_github : :class:`bool`, optional
        Whether to show the MSL packages that are available as GitHub repositories_.
        The default action is to show the MSL packages that are installed.
    detailed : :class:`bool`, optional
        Whether to show detailed information about the MSL packages that are available
        as GitHub repositories_ (i.e., displays additional information about the
        branches and tags). Only used if `from_github` is :obj:`True`.
    from_pypi : :class:`bool`, optional
        Whether to show the MSL packages that are available on PyPI_. The default
        action is to show the MSL packages that are installed.
    update_cache : :class:`bool`, optional
        The information about the MSL packages_ that are available on PyPI_ and about
        the repositories_ that are available on GitHub are cached to use for subsequent
        calls to this function. After 24 hours the cache is automatically updated. Set
        `update_cache` to be :obj:`True` to force the cache to be updated when you call
        this function.
    """
    if from_github:
        typ, pkgs = 'Repository', github(update_cache)
        if not pkgs:
            return
    elif from_pypi:
        typ, pkgs = 'PyPI Package', pypi(update_cache)
        if not pkgs:
            return
    else:
        typ, pkgs = 'Package', installed()

    if detailed and from_github:
        print('')
        indent = '    '
        for p in pkgs:
            print(p + ':')
            for key in sorted(pkgs[p]):
                value = pkgs[p][key]
                print(indent + key + ':')
                if not value:
                    continue
                if not isinstance(value, list):
                    value = [value]
                print(indent + indent + ('\n' + indent + indent).join(v for v in value))
        return

    # determine the maximum width of each column
    header = ['MSL ' + typ, 'Version', 'Description']
    w = [len(h) for h in header]
    for p in pkgs:
        w = [
            max(w[0], len(p)),
            max(w[1], len(pkgs[p]['version'])),
            max(w[2], len(pkgs[p]['description']))
        ]

    # print the results
    print('')
    print(' '.join(header[i].ljust(w[i]) for i in range(len(header))))
    print(' '.join('-' * w for w in w))
    for p in sorted(pkgs):
        print(p.ljust(w[0]) + ' ' + pkgs[p]['version'].ljust(w[1]) + ' ' + pkgs[p]['description'].ljust(w[2]))
