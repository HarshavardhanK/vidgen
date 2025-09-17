#!/usr/bin/env python3
#simple SQLAlchemy Core helper

import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


_engine: Engine | None = None


def get_engine() -> Engine:
    #reads DATABASE_URL
    global _engine
    
    if _engine is None:
        dsn = os.getenv("DATABASE_URL")
        
        if not dsn:
            raise RuntimeError("DATABASE_URL not set")
        
        _engine = create_engine(dsn, pool_pre_ping=True, future=True)
        
    return _engine



