-- Runs once, only when the data volume is created for the first time.
-- Schema changes belong in Alembic migrations, not here.
CREATE EXTENSION IF NOT EXISTS vector;
