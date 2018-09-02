'''
Given an untrusted script, run it in a more secure fashon.

The goal is to eventually use this space to run scripts in a chroot jail
or in a virtual container. Until then, it acts as a middleman.
'''
import subprocess
import sys
from constants import VALID_EXTENSIONS


def main(filepath):
    print(subprocess.check_output(VALID_EXTENSIONS[filepath.split('.')[-1]](filepath), timeout=1).decode('UTF-8'),end='')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
