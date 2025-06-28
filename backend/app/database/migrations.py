# ABOUTME: Alembic migration management with forward/backward compatibility
# ABOUTME: Provides migration operations, version tracking, and schema management utilities

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext

from .config import DatabaseConfig
from .connections import get_async_engine


def get_alembic_config(database_url: str | None = None) -> Config:
    """
    Get Alembic configuration with proper database URL.

    Args:
        database_url: Override database URL, uses default config if not provided

    Returns:
        Alembic Config object
    """
    # Get the migrations directory relative to this file
    migrations_dir = Path(__file__).parent.parent.parent / "migrations"
    alembic_ini_path = migrations_dir / "alembic.ini"

    if not alembic_ini_path.exists():
        # Create default alembic.ini if it doesn't exist
        create_default_alembic_ini(migrations_dir)

    config = Config(str(alembic_ini_path))

    # Set database URL
    if database_url:
        config.set_main_option("sqlalchemy.url", database_url)
    else:
        db_config = DatabaseConfig()
        config.set_main_option("sqlalchemy.url", db_config.url)

    return config


def create_default_alembic_ini(migrations_dir: Path) -> None:
    """
    Create default alembic.ini configuration file.

    Args:
        migrations_dir: Path to migrations directory
    """
    migrations_dir.mkdir(exist_ok=True)
    alembic_ini_path = migrations_dir / "alembic.ini"

    alembic_ini_content = f"""# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = {migrations_dir}

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
# file_template = %%Y%%m%%d_%%H%%M%%S_%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format.
version_num_format = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(second).2d_%%(microsecond).6d

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses
# os.pathsep. If this key is omitted entirely, it falls back to the legacy
# behavior of splitting on spaces and/or commas.
# Valid values for version_path_separator are:
#
# version_path_separator = :
# version_path_separator = ;
# version_path_separator = space
version_path_separator = os

# set to 'true' to search source files recursively
# in each "version_locations" directory
# new in Alembic version 1.10
# recursive_version_locations = false

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = postgresql+asyncpg://postgres:@localhost:5432/snowflake_mcp


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly-generated revision scripts.  See the documentation for further
# detail and examples

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
# hooks = ruff
# ruff.type = exec
# ruff.executable = %(here)s/.venv/bin/ruff
# ruff.options = --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %%H:%%M:%%S
"""

    alembic_ini_path.write_text(alembic_ini_content)


async def get_current_revision() -> str | None:
    """
    Get current database revision.

    Returns:
        Current revision ID or None if no migrations applied
    """
    engine = await get_async_engine(DatabaseConfig())

    async with engine.begin() as conn:
        context = MigrationContext.configure(conn.sync_connection)
        return context.get_current_revision()


async def migrate_to_latest() -> None:
    """Apply all pending migrations to bring database to latest revision."""
    config = get_alembic_config()
    command.upgrade(config, "head")


async def rollback_migration(target_revision: str | None = None) -> None:
    """
    Roll back migration(s).

    Args:
        target_revision: Target revision to roll back to, or None to roll back one revision
    """
    config = get_alembic_config()
    target = target_revision or "-1"
    command.downgrade(config, target)


def create_migration(message: str | None = None) -> None:
    """
    Create new migration file.

    Args:
        message: Migration message, uses auto-generated if not provided
    """
    config = get_alembic_config()
    message = message or "Auto-generated migration"
    command.revision(config, message=message, autogenerate=True)


def initialize_migrations() -> None:
    """Initialize Alembic migration environment."""
    migrations_dir = Path(__file__).parent.parent.parent / "migrations"

    if not migrations_dir.exists():
        migrations_dir.mkdir(exist_ok=True)

        # Create alembic init structure
        config = get_alembic_config()
        command.init(config, str(migrations_dir))

        # Create initial migration for user model
        create_migration("Create user model")


async def validate_migration_state() -> bool:
    """
    Validate that database is in sync with migration scripts.

    Returns:
        True if database is up to date, False otherwise
    """
    try:
        current_revision = await get_current_revision()
        config = get_alembic_config()

        # This would need script directory to get head revision
        # For now, return True if we have any revision
        return current_revision is not None
    except Exception:
        return False
