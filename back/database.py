from sqlalchemy import create_engine, MetaData


meta = MetaData()


def get_engine():
    return create_engine('mysql+pymysql://root:root@localhost:3306/adt')


def get_conn(engine):
    return engine.connect()


def connect_to_DB():
    engine = create_engine('mysql+pymysql://root:root@localhost:3306/adt')
    meta = MetaData()
    conn = engine.connect()
    return engine, meta, conn
