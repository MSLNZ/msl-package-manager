"""
Shows the list of MSL packages that are available.
"""
from .helper import github
from .helper import installed


def show(from_github=False):
    """
    Shows the list of MSL packages that are available.

    Args:
        from_github (bool, optional): Whether to show the MSL packages that are available as
            GitHub_ repositories, :py:data:`True`, or the MSL packages that are installed,
            :py:data:`False`. Default is to show the MSL packages that are installed.

    .. _GitHub: https://github.com/MSLNZ
    """
    if from_github:
        typ, pkgs = 'Repositories', github()
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
