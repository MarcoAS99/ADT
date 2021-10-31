from sqlalchemy import create_engine, MetaData

engine = create_engine('mysql+pymysql://root:root@localhost:3306/adt')
meta = MetaData()
conn = engine.connect()
