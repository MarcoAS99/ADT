from abc import abstractmethod
from pydantic import BaseModel
from sqlalchemy.engine.base import Connection
import re
import hashlib


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
        query = f"""SELECT COUNT(email) AS cont FROM User WHERE email LIKE '{email}';"""
        res = conn.execute(query)
        if(res.first()['cont'] <= 0):
            self.error_list.append('User not registered.')
            return False
        query = f"""SELECT pwd FROM User WHERE email LIKE '{email}';"""
        res = conn.execute(query)
        if hashlib.md5(pwd.encode()).hexdigest() != res.first()['pwd']:
            self.error_list.append('Email or Password incorrect.')
            return False
        return True

    async def validate(self, conn: Connection, email: str):
        query = f"""UPDATE User SET validated=TRUE WHERE email LIKE '{email}'"""
        res = conn.execute(query).rowcount
        if res <= 0:
            return False
        return True
