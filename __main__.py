import sys

from naabal.scripts.big import MAIN_IDX

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main = MAIN_IDX[sys.argv[1]]
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        main()
    else:
        sys.stdout.write('Usage: {0} <{1}> ...\n'.format(sys.argv[0], ', '.join(MAIN_IDX.keys())))
