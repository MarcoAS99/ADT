from pydantic import BaseModel
import re


class User(BaseModel):
    error_list = []

    async def is_valid(self, name: str, email: str, phone: int, password: str):
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
            return True
        return False

    async def register(self, name: str, email: str, phone: int, password: str, paymentMode: str):
        if await self.is_valid(name, email, phone, password):
            # TODO: METER DATOS DE USUARIO EN BBDD
            print('OK')
            return True
        else:
            return False
