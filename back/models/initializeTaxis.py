import json
from sqlalchemy.engine.base import Connection
import time
from geopy.geocoders import Nominatim

client = Nominatim(user_agent='tutorial')


def get_coord_by_address(address):
    """This function returns a location as raw from an address
    will repeat until success"""
    time.sleep(1)
    try:
        location = client.geocode(f'{address}, Madrid').raw
        coord = (location['lat'], location['lon'])
        return coord
    except:
        return get_coord_by_address(address)


def create_taxis(conn: Connection):
    cond = """SELECT count(*) AS cont FROM Taxi"""
    cond_res = conn.execute(cond)
    if cond_res.first()['cont'] > 0:
        return

    with open('./db/taxis.json', 'r') as f:
        taxis = json.load(f)

    for taxi in taxis:
        coords_origen = get_coord_by_address(taxi['ubicacion'])

        query = f"""INSERT INTO Taxi(estado,ubicacion,lon_ubi,lat_ubi) 
        VALUES('{taxi['estado']}','{taxi['ubicacion']}','{coords_origen[1]}','{coords_origen[0]}')"""
        conn.execute(query)
# sitio:{nombre} --> coords{sitio}
