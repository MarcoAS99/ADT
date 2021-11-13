from abc import abstractmethod
from pydantic import BaseModel
from sqlalchemy.engine.base import Connection
import re
import hashlib
import numpy as np

from models.initializeTaxis import get_coord_by_address


class User_model(BaseModel):
    error_list = []

    async def is_valid(self, conn: Connection, name: str, email: str, phone: int, password: str):
        print('Inicio is valid')
        if len(name) > 50:
            self.error_list.append('Username max chars is 50.')
        if not (email.__contains__("@")):
            self.error_list.append('Email format wrong.')
        if len(phone) != 9:
            self.error_list.append('Length of phone number incorrect.')
        if not re.match(r"^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[@#$])[\w\d@#$]{6,16}$", password):
            self.error_list.append(
                'Password must contain at least one digit, one uppercase letter, one lowercase letter, one special character and have a length between 6 and 16.')
        if not self.error_list:
            query = f"""SELECT COUNT(email) AS cont FROM User WHERE email LIKE '{email}';"""
            res = conn.execute(query)
            if(res.first()['cont'] <= 0):
                return True
            self.error_list.append('User already exists.')
        return False

    async def register(self, conn: Connection, name: str, email: str, phone: int, password: str, paymentMode: str):
        if await self.is_valid(conn, name, email, phone, password):
            query = f"""INSERT INTO User(nombre,email,tlf,pwd,privileges,paymethod,validated)
                      values ('{name}','{email}',{phone},'{hashlib.md5(password.encode()).hexdigest()}',0,'{paymentMode}', False);"""
            conn.execute(query)
            return True
        else:
            return False

    async def login(self, conn: Connection, email: str, pwd: str):
        query = f"""SELECT COUNT(email) AS cont, validated FROM User WHERE email LIKE '{email}'
                    GROUP BY validated;"""
        res = conn.execute(query).mappings().all()
        print(res)
        if(res[0]['cont'] <= 0):
            self.error_list.append('User not registered.')
            return False
        if(not res[0]['validated']):
            self.error_list.append(
                'User not validated, please check your email.')
            return False
        query = f"""SELECT pwd FROM User WHERE email LIKE '{email}';"""
        res = conn.execute(query)
        if hashlib.md5(pwd.encode()).hexdigest() != res.first()['pwd']:
            self.error_list.append('Email or Password incorrect.')
            return False
        return True

    async def validate(self, conn: Connection, email: str):
        query = f"""SELECT email FROM User WHERE validated=FALSE;"""
        aux = conn.execute(query).mappings().all()
        print(aux)
        for cursor in aux:
            print(cursor['email'])
            if email == cursor['email']:
                query = f"""UPDATE User SET validated=TRUE WHERE email LIKE '{email}'"""
                res = conn.execute(query).rowcount
                if res > 0:
                    return True
        return False

    async def is_admin(self, conn: Connection, email: str):
        query = f"""SELECT privileges FROM User WHERE email LIKE '{email}';"""
        res = conn.execute(query).mappings().all()
        print(res)
        if res != []:
            return res[0]['privileges']
        return 0

    async def getId(self, conn: Connection, email_hash: str):
        query = f"""SELECT id,email FROM User;"""
        aux = conn.execute(query).mappings().all()
        if aux != []:
            for u in aux:
                if hashlib.md5(u['email'].encode()).hexdigest() == email_hash:
                    return True, u['id']
        return False, None


class Request_model(BaseModel):
    error_list = []

    async def bestTaxi(self, origin_coord, free_taxis):
        best = None
        for key, value in free_taxis.items():
            dist = self.dist_between_2_p(
                (float(origin_coord[0]), float(origin_coord[1])), (float(value[0]), float(value[1])))
            if best is None:
                best = (key, dist)
            elif best[1] > dist:
                best = (key, dist)
        return best[0]

    def dist_between_2_p(self, origin, dest):
        return ((((dest[0] - origin[0])**2) + ((dest[1]-origin[1])**2))**0.5)

    async def request(self, conn: Connection, origin: str, destination: str):
        origin_coord = get_coord_by_address(origin)
        destination_coord = get_coord_by_address(destination)

        query = "SELECT id, lon_ubi, lat_ubi FROM Taxi WHERE estado LIKE 'free'"
        aux = conn.execute(query).mappings().all()
        if aux != []:
            free_taxis = {}
            for taxi in aux:
                free_taxis[taxi['id']] = (taxi['lat_ubi'], taxi['lon_ubi'])
            best_taxi = await self.bestTaxi(origin_coord, free_taxis)
            return True, best_taxi
        return False, None

    async def postRequest(self, conn: Connection, id_user: int, id_taxi: int, origen: str, destino: str, date: str, time: str):
        query = f"""INSERT INTO Solicitud(id_user,id_taxi,origen,destino,datenow,estado)
                    VALUES('{id_user}','{id_taxi}','{origen}','{destino}','{date} {time}:00', 'pending');"""
        conn.execute(query)

    async def check_pending_requests(self, conn: Connection):
        query = f"""SELECT * FROM Solicitud WHERE estado LIKE 'pending';"""
        res = conn.execute(query).mappings().all()
        return res

    async def update(self, conn: Connection, id_req: int, estado: str):
        query = f"""UPDATE Solicitud SET estado = '{estado}' WHERE id = {id_req}"""
        res = conn.execute(query).rowcount
        if res > 0 and estado == 'accepted':
            return True
        return False


class Taxi_Model(BaseModel):

    async def update(self, conn: Connection, id_taxi: int):
        query = f"""UPDATE Taxi SET estado = 'busy' WHERE id = {id_taxi}"""
        res = conn.execute(query).rowcount
        if res > 0:
            return True
        return False
