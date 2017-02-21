"""
Show the list of MSL packages that are available.
"""
from .helper import github
from .helper import installed


def show(from_github=False, github_release_info=False):
    """
    Show the list of MSL packages that are available.

    Args:
        from_github (bool, optional): Whether to show the MSL packages that are available as
            GitHub_ repositories, :py:data:`True`, or the MSL packages that are installed,
            :py:data:`False`. Default is to show the MSL packages that are installed.

        github_release_info (bool, optional): Whether to fetch the release information from the
            GitHub_ repositories. Getting the release information takes longer to execute the
            request. This argument is only used if ``from_github`` is :py:data:`True`. The
            release information is always included for installed packages. Default is to ignore
            the release information from GitHub_.

    .. _GitHub: https://github.com/MSLNZ
    """
    if from_github:
        typ, pkgs = 'Repositories', github(github_release_info)
    else:
        typ, pkgs = 'Packages', installed()

    # determine the maximum width of each column
    header = ['MSL ' + typ, 'Version', 'Description']
    widths = [len(h) for h in header]
    for p in pkgs:
        widths = [max(widths[0], len(p)), max(widths[1], len(pkgs[p][0])), max(widths[1], len(pkgs[p][1]))]

    # print the results
    print(' '.join(header[i].ljust(widths[i]) for i in range(len(header))))
    print(' '.join('-' * w for w in widths))
    for p in sorted(pkgs):
        print(p.ljust(widths[0]) + ' ' + pkgs[p][0].ljust(widths[1]) + ' ' + pkgs[p][1].ljust(widths[2]))
