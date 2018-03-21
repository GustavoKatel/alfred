# -*- coding: utf-8 -*-

"""Console script for alfred."""
import sys
from alfred import Alfred


def main(args=None):
    """Console script for alfred."""
    if args is None:
        args = sys.argv[1:]

    al = Alfred()
    return al.run(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv))  # pragma: no cover
