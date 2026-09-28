from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

from app import models
from app.database import Base, DATABASE_URL

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

PRODUCT_VERSION_TABLE = "alembic_version"


def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = DATABASE_URL.render_as_string(hide_password=True)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table=PRODUCT_VERSION_TABLE,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode."""
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        pool_pre_ping=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=PRODUCT_VERSION_TABLE,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
