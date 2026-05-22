from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    apellido: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
   
    favoritos: Mapped[List["Favoritos"]] = relationship("Favoritos", back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "email": self.email
        }

class Marvel(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_heroe: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    nivel_poder: Mapped[int] = mapped_column(Integer, nullable=False)
    afiliacion: Mapped[str] = mapped_column(String(120), nullable=False)

    favoritos: Mapped[List["Favoritos"]] = relationship("Favoritos", back_populates="marvel")

    def serialize(self):
        return {
            "id": self.id,
            "nombre_heroe": self.nombre_heroe,
            "nivel_poder": self.nivel_poder,
            "afiliacion": self.afiliacion,
        }

class Dc(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_heroe: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    apariciones_comics: Mapped[int] = mapped_column(Integer, nullable=False)
    ciudad_base: Mapped[str] = mapped_column(String(120), nullable=False) 

    favoritos: Mapped[List["Favoritos"]] = relationship("Favoritos", back_populates="dc")

    def serialize(self):
        return {
            "id": self.id,
            "nombre_heroe": self.nombre_heroe,
            "apariciones_comics": self.apariciones_comics,
            "ciudad_base": self.ciudad_base,
        }

class Other(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_heroe: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    universo_origen: Mapped[str] = mapped_column(String(120), nullable=False)
    año_creacion: Mapped[int] = mapped_column(Integer, nullable=False)

    favoritos: Mapped[List["Favoritos"]] = relationship("Favoritos", back_populates="other")

    def serialize(self):
        return {
            "id": self.id,
            "nombre_heroe": self.nombre_heroe,
            "universo_origen": self.universo_origen,
            "año_creacion": self.año_creacion
        }

class Favoritos(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    id_marvel: Mapped[int] = mapped_column(ForeignKey("marvel.id"), nullable=True)
    id_dc: Mapped[int] = mapped_column(ForeignKey("dc.id"), nullable=True)
    id_other: Mapped[int] = mapped_column(ForeignKey("other.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="favoritos")
    marvel: Mapped["Marvel"] = relationship("Marvel", back_populates="favoritos")
    dc: Mapped["Dc"] = relationship("Dc", back_populates="favoritos")
    other: Mapped["Other"] = relationship("Other", back_populates="favoritos")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "id_marvel": self.id_marvel,
            "id_dc": self.id_dc,
            "id_other": self.id_other,
            "marvel": self.marvel.serialize() if self.marvel else None,
            "dc": self.dc.serialize() if self.dc else None,
            "other": self.other.serialize() if self.other else None
        }