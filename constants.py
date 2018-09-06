"""
Constant values go here
"""
import os


PROBLEMS = list(range(1, 8))

VALID_EXTENSIONS = {
    'py': lambda x: ['python3', x],
    'js': lambda x: ['node', x],
    'java': None # lambda x: ['javac', x, '-d', os.path.join(os.path.dirname(__file__), 'instance', 'tmp', 'compiled')]
}

CUSTOM_EXTENSIONS = [
    'java'
]



PROGRAMS = VALID_EXTENSIONS.keys()


def make_instance_folder(app_instance):
    '''
    Create the needed folders
    '''
    incorrect = os.path.join(app_instance, 'programs', 'incorrect')
    tmp = os.path.join(app_instance, 'tmp')
    correct_problems = [os.path.join(
        app_instance, 'programs', 'correct', str(x)) for x in PROBLEMS]

    if not os.path.exists(incorrect):
        os.makedirs(incorrect)
    if not os.path.exists(tmp):
        os.makedirs(tmp)
    [os.makedirs(x) for x in correct_problems if not os.path.exists(x)]


def compare_rows(x, y):
    if x.size < y.size:
        return 1
    if x.size > y.size:
        return -1
    if x.time < y.time:
        return 1
    if x.time > y.time:
        return -1
    return 0
