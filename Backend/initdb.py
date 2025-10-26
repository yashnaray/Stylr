#!/usr/bin/env python3

import os
import subprocess
import sys

filename = "data/local.db"

def run(args):
    code = subprocess.run(args).returncode
    if code:
        sys.exit(code)

def main():
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-r", "--reset", action="store_true", help="delete everything and reinitialize")
    opts, args = parser.parse_args()
    if args:
        parser.error(f"unexpected argument {args[0]!r}")

    with open("init.sql") as file:
        init_sql = file.read()

    if opts.reset:
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass

    # Create tables and other structures
    import sqlite3
    conn = sqlite3.connect(filename)
    try:
        cur = conn.cursor()
        cur.executescript(init_sql)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
