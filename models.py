from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # В базе данных поле называется 'password'
    key = Column(String)

    @property
    def hashed_password(self):
        return self.password

    @hashed_password.setter
    def hashed_password(self, value):
        self.password = value