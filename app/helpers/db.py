from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SCHEMA = "vaxiin"
Base = declarative_base()


def get_db(db_path, for_testing=False):
    if for_testing:
        engine = create_engine("sqlite://")
        path = ":memory:"
    else:
        engine = create_engine(f"sqlite:///{db_path}/vaxiin.db")
        path = f"{db_path}/vaxiin.db"

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @event.listens_for(engine, "connect")
    def connect(dbapi_conn, rec):
        dbapi_conn.execute(f'ATTACH DATABASE "{path}" AS "{SCHEMA}"')

    return engine, SessionLocal
