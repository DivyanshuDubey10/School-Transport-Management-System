"""
NeoYatra — Database Seed Runner
Execute this script to populate your PostgreSQL database with demo routes, buses, parents, and students:
    py seed.py
"""
import os
import sys

# Point to the backend package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
from seed import seed_database

if __name__ == "__main__":
    seed_database()
