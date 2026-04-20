import enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class TipoElemento(enum.Enum):
    PERSONAJE = "personaje"
    PLANETA = "planeta"
    VEHICULO = "vehiculo"

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_usuario: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    correo: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    
    favoritos = relationship("Favorito", back_populates="user", cascade="all, delete-orphan")

    def serialize(self):
        return {
            "id": self.id,
            "nombre_usuario": self.nombre_usuario,
            "correo": self.correo
        }

class Personaje(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    genero: Mapped[str] = mapped_column(String)
    
    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "genero": self.genero
        }

class Planeta(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    clima: Mapped[str] = mapped_column(String)

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "clima": self.clima
        }

class Vehiculo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    modelo: Mapped[str] = mapped_column(String)

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "modelo": self.modelo
        }

class Favorito(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    tipo_elemento: Mapped[TipoElemento] = mapped_column(Enum(TipoElemento, native_enum=False), nullable=False) 
    elemento_id: Mapped[int] = mapped_column(nullable=False)

    user = relationship("User", back_populates="favoritos")
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tipo_elemento": self.tipo_elemento.value,
            "elemento_id": self.elemento_id
        }