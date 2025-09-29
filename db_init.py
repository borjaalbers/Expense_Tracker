"""
Utility to create database tables.

Run:
  python db_init.py
"""
from db import ENGINE
from models import Base


def main() -> None:
    Base.metadata.create_all(bind=ENGINE)
    print("Database tables created.")


if __name__ == "__main__":
    main()


