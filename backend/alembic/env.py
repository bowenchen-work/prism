from alembic import context
from sqlalchemy import engine_from_config, pool
import os

config = context.config

config.set_section_option("alembic", "DB_USER", os.getenv("DB_USER", "prism_user"))
config.set_section_option("alembic", "DB_PASSWORD", os.getenv("DB_PASSWORD", "changeme"))
config.set_section_option("alembic", "DB_HOST", os.getenv("DB_HOST", "db"))
config.set_section_option("alembic", "DB_NAME", os.getenv("DB_NAME", "prism"))

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()