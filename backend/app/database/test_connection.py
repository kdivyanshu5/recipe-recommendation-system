from sqlalchemy import text
from db import engine

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))

    for row in result:
        print(row)