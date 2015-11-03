#!/usr/bin/env python3
import sys

from riley.management import ManagementUtility


def main():
    ManagementUtility().execute(sys.argv)


if __name__ == '__main__':
    main()
