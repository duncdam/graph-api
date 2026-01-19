from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class Neo4j(BaseSettings):
    """Neo4j database configuration settings."""

    uri: Optional[str] = Field(None, description="Neo4j connection URI")
    username: Optional[str] = Field(None, description="Neo4j username")
    password: Optional[str] = Field(None, description="Neo4j password")
    database: Optional[str] = Field(None, description="Neo4j database name")

    class Config:
        env_prefix = "NEO4J_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        fields = {
            "uri": {"env": "NEO4J_URI"},
            "username": {"env": "NEO4J_USERNAME"},
            "password": {"env": "NEO4J_PASSWORD"},
            "database": {"env": "NEO4J_DATABASE"},
        }


class Postgres(BaseSettings):
    """PostgreSQL database configuration settings."""

    host: Optional[str] = Field(None, description="PostgreSQL host")
    port: Optional[str] = Field(None, description="PostgreSQL port")
    database: Optional[str] = Field(None, description="PostgreSQL database name")
    user: Optional[str] = Field(None, description="PostgreSQL username")
    password: Optional[str] = Field(None, description="PostgreSQL password")

    class Config:
        env_prefix = "DB_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        fields = {
            "host": {"env": "DB_HOST"},
            "port": {"env": "DB_PORT"},
            "database": {"env": "DB_NAME"},
            "user": {"env": "DB_USER"},
            "password": {"env": "DB_PASSWORD"},
        }


neo4j = Neo4j()
postgres = Postgres()
