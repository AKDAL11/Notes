"""initial migration

Revision ID: 6f24e4f0eeea
Revises: 
Create Date: 2025-02-27 11:02:48.812958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f24e4f0eeea'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# DB_NAME = "notes.db"

# class DatabaseSQLite:
    # def __init__(self, db_name: str = DB_NAME):
    #     self.db_name = db_name
    #     self.init_db()

    # def connect(self):
    #     """Подключение к базе данных"""
    #     return sqlite3.connect(self.db_name)

def upgrade() -> None:
    
    op.execute("""
       ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'USER'  CHECK (role IN ('USER','ADMIN'))
""")


def downgrade() -> None:
     op.execute("""
    ALTER TABLE users
    DROP COLUMN role;
    """)
    
