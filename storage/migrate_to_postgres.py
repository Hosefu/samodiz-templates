#!/usr/bin/env python
"""
Simple script to help migrate data from SQLite to PostgreSQL.
This script dumps the database from SQLite as JSON fixtures and loads them into PostgreSQL.
"""

import os
import subprocess
import argparse

def run_command(command):
    """Run a shell command and print output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=True)
    return result.returncode == 0

def dump_data_from_sqlite():
    """Dump data from SQLite database as JSON fixtures"""
    if not os.path.exists("fixtures"):
        os.makedirs("fixtures")
    
    apps = ["auth", "templates"]
    
    for app in apps:
        print(f"Dumping data from {app}...")
        run_command(f"python manage.py dumpdata {app} --indent 2 > fixtures/{app}.json")
    
    print("Data dumped successfully to 'fixtures/' directory")

def load_data_to_postgres():
    """Load data from JSON fixtures to PostgreSQL database"""
    fixture_dir = "fixtures"
    if not os.path.exists(fixture_dir):
        print("No fixtures directory found. Run dump_data_from_sqlite first.")
        return False
    
    fixtures = sorted([f for f in os.listdir(fixture_dir) if f.endswith('.json')])
    
    if not fixtures:
        print("No fixture files found in 'fixtures/' directory")
        return False
    
    print("Applying migrations...")
    run_command("python manage.py migrate")
    
    for fixture in fixtures:
        fixture_path = os.path.join(fixture_dir, fixture)
        print(f"Loading fixture: {fixture_path}")
        run_command(f"python manage.py loaddata {fixture_path}")
    
    print("Data loaded successfully to PostgreSQL")
    return True

def main():
    parser = argparse.ArgumentParser(description="Migrate data from SQLite to PostgreSQL")
    parser.add_argument('--dump', action='store_true', help='Dump data from SQLite')
    parser.add_argument('--load', action='store_true', help='Load data to PostgreSQL')
    
    args = parser.parse_args()
    
    if args.dump:
        dump_data_from_sqlite()
    
    if args.load:
        load_data_to_postgres()
    
    if not args.dump and not args.load:
        print("Please specify --dump or --load")
        parser.print_help()

if __name__ == "__main__":
    main() 