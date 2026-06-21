#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

This file was cleaned to remove duplicated blocks. It defaults to
using `tattoo_finance.settings`. To override, set the
`DJANGO_SETTINGS_MODULE` environment variable before running.
"""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tattoo_finance.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
