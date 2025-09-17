#!/usr/bin/env python3
#simple SQLAlchemy Core helper

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from .config import config


_engine: Engine | None = None


def get_engine() -> Engine:
    #reads DATABASE_URL from config
    global _engine
    
    if _engine is None:
        dsn = config.DATABASE_URL
        
        if not dsn:
            raise RuntimeError("DATABASE_URL not set")
        
        _engine = create_engine(dsn, pool_pre_ping=True, future=True)
        
    return _engine



