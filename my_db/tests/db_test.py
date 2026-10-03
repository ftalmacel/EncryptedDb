import pytest
from sqlalchemy import text

from src.db import DbConnectionPool, create_tables


@pytest.fixture
def test_same_engine():
    db_url = "sqlite:///my_db.db"

    pool1 = DbConnectionPool(db_url)
    pool2 = DbConnectionPool(db_url)

    assert pool1.pool_engine is pool2.pool_engine


def test_table_created():
    DbConnectionPool._instance = None

    db_url = "sqlite:///:memory:"
    pool = DbConnectionPool(db_url=db_url)

    create_tables(pool.engine())

    with pool.engine().connect() as conn:
        x = conn.execute(text("SELECT * FROM files")).fetchall()

    assert x == []
