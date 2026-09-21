"""
PostgreSQL Connection Pool Manager.
Uses psycopg2.pool.ThreadedConnectionPool with resilient offline fallback.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator, Optional

try:
    import psycopg2
    from psycopg2 import pool
    _PSYCOPG2_AVAILABLE = True
except ImportError:
    psycopg2 = None
    pool = None
    _PSYCOPG2_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger("db.connection")


class PostgresConnectionManager:
    """
    Thread-safe connection pool manager for PostgreSQL.
    Provides graceful offline fallback when PostgreSQL is not running.
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        minconn: int = 1,
        maxconn: int = 10,
    ):
        self.database_url = database_url or settings.DATABASE_URL
        self.minconn = minconn
        self.maxconn = maxconn
        self._pool: Optional[pool.ThreadedConnectionPool] = None
        self._is_connected: bool = False
        self._init_pool()

    def _init_pool(self) -> None:
        if not _PSYCOPG2_AVAILABLE:
            logger.info("psycopg2 is not available. Operating in offline database mode.")
            self._is_connected = False
            return

        try:
            self._pool = pool.ThreadedConnectionPool(
                self.minconn,
                self.maxconn,
                dsn=self.database_url,
                connect_timeout=2,
            )
            # Verify pool works by checking out a connection
            conn = self._pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                conn.commit()
                self._is_connected = True
                logger.info("PostgreSQL connection pool initialized successfully.")
            finally:
                self._pool.putconn(conn)
        except Exception as e:
            self._pool = None
            self._is_connected = False
            logger.info(
                f"PostgreSQL not reachable at {self.database_url} ({e}). "
                "Operating in resilient offline database mode."
            )

    @property
    def is_connected(self) -> bool:
        if not self._pool:
            return False
        try:
            conn = self._pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
                conn.commit()
                self._is_connected = True
                return True
            finally:
                self._pool.putconn(conn)
        except Exception:
            self._is_connected = False
            return False

    @contextmanager
    def get_connection(self) -> Generator[Optional[Any], None, None]:
        """
        Context manager that yields a PostgreSQL connection from the pool.
        Handles commit on success, rollback on error, and always returns
        the connection to the pool. Yields None if offline.
        """
        if not self._pool:
            yield None
            return

        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.warning(f"Database transaction error: {e}")
            raise
        finally:
            if conn and self._pool:
                try:
                    self._pool.putconn(conn)
                except Exception:
                    pass

    def close(self) -> None:
        """Closes all connections in the pool."""
        if self._pool:
            try:
                self._pool.closeall()
                self._pool = None
                self._is_connected = False
                logger.info("PostgreSQL connection pool closed.")
            except Exception as e:
                logger.warning(f"Error closing PostgreSQL pool: {e}")
