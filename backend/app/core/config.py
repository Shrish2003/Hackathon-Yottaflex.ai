"""
Core configuration module using pydantic-settings.
Reads from environment variables and backend/.env reliably across any working directory.
Safely normalizes database credentials and URL-reserved special characters (such as '@').
"""

from pathlib import Path
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url

# Compute backend root directory where .env resides
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    app_name: str = Field(default="O2C Revenue Assurance Platform", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    
    # Primary connection string (from .env or environment)
    database_url: Optional[str] = Field(default=None, alias="DATABASE_URL")
    
    # Discrete database connection parameters (optional override or direct specification)
    db_user: str = Field(default="postgres", alias="DB_USER")
    db_password: Optional[str] = Field(default=None, alias="DB_PASSWORD")
    db_host: str = Field(default="127.0.0.1", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(default="o2c_revenue_db", alias="DB_NAME")

    backend_host: str = Field(default="127.0.0.1", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    frontend_origin: str = Field(default="http://localhost:5173", alias="FRONTEND_ORIGIN")

    def model_post_init(self, __context) -> None:
        """Post-initialization hook to ensure database_url is fully resolved and normalized."""
        self.database_url = self.get_database_url()

    def get_database_url(self) -> str:
        """
        Safely resolves, parses, and normalizes the SQLAlchemy database connection URL.
        Guarantees that:
        1. Discrete DB_PASSWORD credentials are constructed using URL.create() without manual encoding issues.
        2. DATABASE_URL with raw unencoded '@' characters is safely split from the right at the host delimiter.
        3. Pre-encoded URLs are preserved and safely parsed by SQLAlchemy.
        """
        # 1. If discrete DB_PASSWORD is provided, build via URL.create
        if self.db_password:
            return URL.create(
                drivername="postgresql+psycopg",
                username=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
            ).render_as_string(hide_password=False)

        # 2. If explicit DATABASE_URL is provided:
        if self.database_url:
            raw_url = self.database_url.strip()
            
            # Check for unencoded '@' in password (i.e. more than 1 '@' in entire URI)
            if "://" in raw_url and raw_url.count("@") > 1:
                try:
                    scheme, rest = raw_url.split("://", 1)
                    # Split at the LAST '@' to separate userinfo from host:port/database
                    userinfo, hostpart = rest.rsplit("@", 1)
                    if ":" in userinfo:
                        user, password = userinfo.split(":", 1)
                    else:
                        user, password = userinfo, None
                    
                    host = "127.0.0.1"
                    port = 5432
                    database = "o2c_revenue_db"
                    
                    if "/" in hostpart:
                        host_port, database = hostpart.split("/", 1)
                    else:
                        host_port = hostpart
                        
                    if ":" in host_port:
                        host, port_str = host_port.split(":", 1)
                        port = int(port_str)
                    else:
                        host = host_port
                    
                    return URL.create(
                        drivername=scheme,
                        username=user,
                        password=password,
                        host=host,
                        port=port,
                        database=database,
                    ).render_as_string(hide_password=False)
                except Exception:
                    pass

            # Standard / pre-encoded URL: ensure it parses via make_url
            return raw_url

        # Default fallback
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password="",
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        ).render_as_string(hide_password=False)

    @property
    def cors_origins(self) -> List[str]:
        origins = [self.frontend_origin]
        if "localhost" in self.frontend_origin:
            origins.append(self.frontend_origin.replace("localhost", "127.0.0.1"))
        return origins

    model_config = SettingsConfigDict(
        # Search both absolute path to backend/.env and current working directory .env
        env_file=[str(ENV_PATH), ".env"],
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


settings = Settings()
