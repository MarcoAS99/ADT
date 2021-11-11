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
        location = client.geocode(address).raw
        coord = (location['lat'], location['lon'])
        return coord
    except:
        return get_coord_by_address(address)


address = "Miguel Solas"
coords = get_coord_by_address(address)
latitude = coords[0]
longitude = coords[1]
print(f"{latitude}, {longitude}")


def create_taxis(conn: Connection):
    cond = """SELECT count(*) AS cont FROM Taxi"""
    cond_res = conn.execute(cond)
    if cond_res.first()['cont'] > 0:
        return

    with open('./db/taxis.json', 'r') as f:
        taxis = json.load(f)

    for taxi in taxis:
        query = f"""INSERT INTO Taxi(estado,ubicacion,destino) 
        VALUES('{taxi['estado']}','{taxi['ubicacion']}','{taxi['destino']}')"""
        conn.execute(query)
# sitio:{nombre} --> coords{sitio}
