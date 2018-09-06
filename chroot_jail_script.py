'''
Given an untrusted script, run it in a more secure fashon.

The goal is to eventually use this space to run scripts in a chroot jail
or in a virtual container. Until then, it acts as a middleman.
'''
import subprocess
import sys
import os
import time
from shutil import copyfile
from constants import VALID_EXTENSIONS, CUSTOM_EXTENSIONS


def main(filepath):

    if filepath.split('.')[-1] not in CUSTOM_EXTENSIONS:
        print(subprocess.check_output(VALID_EXTENSIONS[filepath.split('.')[-1]](filepath), timeout=1).decode('UTF-8'),end='')
    else:
        # Todo move this logic into a new function or somewhere not in this function
        
        custom_folder = str(time.time()).replace('.', '-')

        folder_path = os.path.join(os.path.dirname(__file__), 'instance', 'tmp', custom_folder)

        os.makedirs(folder_path)

        new_filepath = os.path.join(folder_path, ''.join(os.path.basename(filepath).split('-')[2:]))

        copyfile(filepath, new_filepath)

        try:
            # run javac
            subprocess.check_output(['javac', new_filepath, '-d', folder_path], timeout=5)

            class_name = os.path.basename(new_filepath).replace('.java', '')

            # run java
            print(subprocess.check_output(['java', '-cp', folder_path, class_name], timeout=1).decode('UTF-8'),end='')
        finally:
            # delete files
            if os.path.exists(new_filepath):
                os.remove(new_filepath)
            if os.path.exists(new_filepath.replace('.java', '.class')):
                os.remove(new_filepath.replace('.java', '.class'))
            # delete folder
            os.rmdir(folder_path)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
