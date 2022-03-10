from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SCHEMA = "vaxiin"
Base = declarative_base()


def get_db(db_path):
    engine = create_engine(f"sqlite:///{db_path}/vaxiin.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @event.listens_for(engine, "connect")
    def connect(dbapi_conn, rec):
        dbapi_conn.execute(f'ATTACH DATABASE "{db_path}/vaxiin.db" AS "{SCHEMA}"')

    return engine, SessionLocal
