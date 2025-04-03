from os import getenv

import sqlalchemy
from sqlmodel import SQLModel, create_engine

import api.utils


engine = create_engine(
    sqlalchemy.URL.create(
        drivername="postgresql",
        username=api.utils.read_secret("POSTGRES_USER"),
        password=api.utils.read_secret("POSTGRES_PASSWORD"),
        database=getenv("POSTGRES_DB"),
        host="db",
        port=5432,
    ),
    echo=getenv("DEBUG") == "True"
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
