from sqlalchemy import Table, Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, DateTime
from database import meta

user = Table(
    'User',
    meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('nombre', String(50), nullable=False),
    Column('email', String(50)),
    Column('tlf', Integer),
    Column('paymethod', String(50)),
    Column('pwd', String(50), nullable=False),
    Column('privileges', Integer),
    extend_existing=True
)

taxi = Table(
    'Taxi',
    meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('estado', String(8)),
    Column('ubicacion', String(100)),
    Column('destino', String(100)),
    extend_existing=True
)

solicitud = Table(
    'Solicitud',
    meta,
    Column('id', Integer, primary_key=True),
    Column('id_user', Integer),
    Column('id_taxi', Integer),
    Column('origen', String(50)),
    Column('destino', String(50)),
    Column('datenow', DateTime),
    Column('estado', String(8)),
    extend_existing=True
)
