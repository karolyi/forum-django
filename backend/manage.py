#!/usr/bin/env python3
import os
import sys

if sys.platform == 'darwin':
    # VERY IMPORTANT FOR OSX, SET PYTHONEXECUTABLE:
    # https://stackoverflow.com/a/53190037/1067833
    sys.executable = sys._base_executable

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "forum.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
