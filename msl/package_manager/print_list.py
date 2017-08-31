"""
Print the list of MSL packages that are available.
"""
from .helper import github
from .helper import installed


def print_list(from_github=False, update_github_cache=False):
    """Print the list of MSL packages that are available.

    The list of packages can be either those that are installed or those that are
    available as repositories_ on GitHub.

    .. _repositories: https://github.com/MSLNZ
    
    Parameters
    ----------
    from_github : :obj:`bool`, optional
        Whether to show the MSL packages that are available as GitHub repositories_
        or the MSL packages that are installed. Default is to show the MSL packages
        that are installed.
    update_github_cache : :obj:`bool`, optional
        The information about the repositories_ that are available on GitHub are
        cached to use for subsequent calls to this function. After 24 hours the
        cache is automatically updated. Set `update_github_cache` to be :obj:`True`
        to force the cache to be updated when you call this function.
    """
    if from_github:
        typ, pkgs = 'Repository', github(update_github_cache)
        if not pkgs:
            return
    else:
        typ, pkgs = 'Package', installed()

    # determine the maximum width of each column
    header = ['MSL ' + typ, 'Version', 'Description']
    widths = [len(h) for h in header]
    for p in pkgs:
        widths = [max(widths[0], len(p)), max(widths[1], len(pkgs[p][0])), max(widths[2], len(pkgs[p][1]))]

    # print the results
    print('')
    print(' '.join(header[i].ljust(widths[i]) for i in range(len(header))))
    print(' '.join('-' * w for w in widths))
    for p in sorted(pkgs):
        print(p.ljust(widths[0]) + ' ' + pkgs[p][0].ljust(widths[1]) + ' ' + pkgs[p][1].ljust(widths[2]))
