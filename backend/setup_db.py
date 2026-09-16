"""
Member 6  DevOps owns this file.

Creates the ghostnet role and the ghostnet database, then checks that the app
can actually connect. Run it once after installing PostgreSQL.

    python setup_db.py

It connects as the postgres superuser first, because a role cannot create
itself. If your superuser password is not postgres, pass it in:

    python setup_db.py --password yourpassword

If the database is somewhere else entirely, skip this script and set
DATABASE_URL instead. See .env.example.
"""

import argparse
import sys

import psycopg

import db


def superuser_url(user, password, host, port):
    # The maintenance database always exists, so it is the safe place to
    # connect while the ghostnet database does not exist yet.
    return "postgresql://%s:%s@%s:%s/postgres" % (user, password, host, port)


def run(args):
    admin = superuser_url(args.user, args.password, args.host, args.port)

    try:
        # Creating a database cannot run inside a transaction block, which is
        # what autocommit is for here.
        with psycopg.connect(admin, autocommit=True) as conn:
            exists = conn.execute(
                "SELECT 1 FROM pg_roles WHERE rolname = %s", ("ghostnet",)
            ).fetchone()
            if exists:
                print("role ghostnet already exists")
            else:
                conn.execute("CREATE ROLE ghostnet LOGIN PASSWORD 'ghostnet'")
                print("created role ghostnet")

            exists = conn.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", ("ghostnet",)
            ).fetchone()
            if exists:
                print("database ghostnet already exists")
            else:
                conn.execute("CREATE DATABASE ghostnet OWNER ghostnet")
                print("created database ghostnet")

    except psycopg.OperationalError as e:
        print()
        print("Could not connect to PostgreSQL as the superuser.")
        print("Check that the server is running and that the password is right.")
        print()
        print("  detail:", str(e).strip().splitlines()[0])
        print()
        print("  tried:", superuser_url(args.user, "***", args.host, args.port))
        return 1

    db.init()
    print()
    print("tables ready")
    print("connection string:", db.DATABASE_URL)
    print()
    print("Next step: python seed.py")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Create the GhostNet database")
    p.add_argument("--user", default="postgres", help="superuser name")
    p.add_argument("--password", default="postgres", help="superuser password")
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", default="5432")
    sys.exit(run(p.parse_args()))
