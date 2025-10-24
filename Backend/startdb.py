#!/usr/bin/env python3

import os
import subprocess
import sys

database_dir = "postgres"

reset_sql = """
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
"""

init_sql = """
CREATE TABLE IF NOT EXISTS users (
    uid int PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    username text UNIQUE NOT NULL,
    password text NOT NULL,
    salt text NOT NULL
);
"""

def run(args):
    code = subprocess.run(args).returncode
    if code:
        sys.exit(code)

def startdb(*, reset=False):
    # Initialize the database directory if it doesn't exist
    try:
        os.mkdir(database_dir)
        run(["initdb",
             "-A", "trust",
             "-U", "postgres",
             "-D", database_dir])
    except FileExistsError:
        pass
    except:
        os.rmdir(database_dir)
        raise

    # Start the server if one was not already running
    if not os.path.exists(database_dir + "/postmaster.pid"):
        run(["pg_ctl", "start",
             "-o", "-p 3031",
             "-l", database_dir + "/postgres.log",
             "-D", database_dir])

    # Create tables and other structures
    import psycopg2
    conn = psycopg2.connect(dbname="postgres", user="postgres", port=3031)
    try:
        cur = conn.cursor()
        if reset:
            cur.execute(reset_sql)
        cur.execute(init_sql)
        conn.commit()
    finally:
        conn.close()

def stopdb():
    if os.path.exists(database_dir + "/postmaster.pid"):
        run(["pg_ctl", "stop", "-D", database_dir])

def main():
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("-s", "--stop", action="store_true", help="stop the database")
    parser.add_option("-r", "--reset", action="store_true", help="delete everything and reinitialize")
    opts, args = parser.parse_args()
    if args:
        parser.error(f"unexpected argument {args[0]!r}")
    if opts.stop:
        stopdb()
    else:
        startdb(reset=opts.reset)

if __name__ == "__main__":
    main()
