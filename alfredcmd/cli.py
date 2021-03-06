# -*- coding: utf-8 -*-

"""Console script for alfred."""
import sys
from alfredcmd import Alfred, AlfredException


def main(args=None):
    """Console script for alfred."""
    if args is None:
        args = sys.argv[1:]

    try:
        al = Alfred()
        return al.run(args)
    except AlfredException as e:
        print('X {}'.format(e))
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))  # pragma: no cover
