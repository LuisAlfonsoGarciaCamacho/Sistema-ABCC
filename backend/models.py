from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

Base = declarative_base()

class Departamento(Base):
    """
    Modelo de la tabla 'departamentos'.

    Attributes:
        numero (str): Número de identificación del departamento.
        nombre (str): Nombre del departamento.
        clases (list): Lista de clases relacionadas con el departamento.
    """
    __tablename__ = "departamentos"
    numero = Column(String(1), primary_key=True)
    nombre = Column(String(50))
    clases = relationship("Clase", back_populates="departamento")

class Clase(Base):
    """
    Modelo de la tabla 'clases'.

    Attributes:
        numero (str): Número de identificación de la clase.
        nombre (str): Nombre de la clase.
        departamento_numero (str): Número de identificación del departamento al que pertenece la clase.
        departamento (Departamento): Relación con el departamento correspondiente.
        familias (list): Lista de familias relacionadas con la clase.
    """
    __tablename__ = "clases"
    numero = Column(String(2), primary_key=True)
    nombre = Column(String(50))
    departamento_numero = Column(String(1), ForeignKey("departamentos.numero"))
    departamento = relationship("Departamento", back_populates="clases")
    familias = relationship("Familia", back_populates="clase")

class Familia(Base):
    """
    Modelo de la tabla 'familias'.

    Attributes:
        numero (str): Número de identificación de la familia.
        nombre (str): Nombre de la familia.
        departamento_numero (str): Número de identificación del departamento al que pertenece la familia.
        clase_numero (str): Número de identificación de la clase a la que pertenece la familia.
        clase (Clase): Relación con la clase correspondiente.
    """
    __tablename__ = "familias"
    numero = Column(String(3), primary_key=True)
    nombre = Column(String(50))
    departamento_numero = Column(String(1), ForeignKey("departamentos.numero"))
    clase_numero = Column(String(2), ForeignKey("clases.numero"))
    clase = relationship("Clase", back_populates="familias")

class Articulo(Base):
    """
    Modelo de la tabla 'articulos'.

    Attributes:
        sku (str): Código SKU del artículo.
        articulo (str): Nombre del artículo.
        marca (str): Marca del artículo.
        modelo (str): Modelo del artículo.
        departamento_numero (str): Número de identificación del departamento al que pertenece el artículo.
        clase_numero (str): Número de identificación de la clase a la que pertenece el artículo.
        familia_numero (str): Número de identificación de la familia a la que pertenece el artículo.
        fecha_alta (date): Fecha de alta del artículo.
        stock (int): Cantidad en stock del artículo.
        cantidad (int): Cantidad disponible del artículo.
        descontinuado (int): Indicador de si el artículo está descontinuado.
        fecha_baja (date): Fecha de baja del artículo.

        departamento (Departamento): Relación con el departamento correspondiente.
        clase (Clase): Relación con la clase correspondiente.
        familia (Familia): Relación con la familia correspondiente.
    """
    __tablename__ = "articulos"
    sku = Column(String(6), primary_key=True, index=True)
    articulo = Column(String(15))
    marca = Column(String(15))
    modelo = Column(String(20))
    departamento_numero = Column(String(1), ForeignKey("departamentos.numero"))
    clase_numero = Column(String(2), ForeignKey("clases.numero"))
    familia_numero = Column(String(3), ForeignKey("familias.numero"))
    fecha_alta = Column(Date)
    stock = Column(Integer)
    cantidad = Column(Integer)
    descontinuado = Column(Integer)
    fecha_baja = Column(Date)

    departamento = relationship("Departamento")
    clase = relationship("Clase")
    familia = relationship("Familia")

class ArticuloBase(BaseModel):
    """
    Modelo base para los artículos.

    Attributes:
        sku (str): Código SKU del artículo.
        articulo (str): Nombre del artículo.
        marca (str): Marca del artículo.
        modelo (str): Modelo del artículo.
        departamento_numero (str): Número de identificación del departamento al que pertenece el artículo.
        clase_numero (str): Número de identificación de la clase a la que pertenece el artículo.
        familia_numero (str): Número de identificación de la familia a la que pertenece el artículo.
        stock (int): Cantidad en stock del artículo.
        cantidad (int): Cantidad disponible del artículo.
    """
    sku: str = Field(..., max_length=6)
    articulo: str = Field(..., max_length=15)
    marca: str = Field(..., max_length=15)
    modelo: str = Field(..., max_length=20)
    departamento_numero: str = Field(..., max_length=1)
    clase_numero: str = Field(..., max_length=2)
    familia_numero: str = Field(..., max_length=3)
    stock: int = Field(..., le=999999999)
    cantidad: int = Field(..., le=999999999)

class ArticuloCreate(ArticuloBase):
    """
    Modelo para la creación de artículos, basado en ArticuloBase.
    """
    pass

class ArticuloUpdate(BaseModel):
    """
    Modelo para la actualización de artículos.

    Attributes:
        articulo (Optional[str]): Nombre del artículo.
        marca (Optional[str]): Marca del artículo.
        modelo (Optional[str]): Modelo del artículo.
        departamento_numero (Optional[str]): Número de identificación del departamento al que pertenece el artículo.
        clase_numero (Optional[str]): Número de identificación de la clase a la que pertenece el artículo.
        familia_numero (Optional[str]): Número de identificación de la familia a la que pertenece el artículo.
        stock (Optional[int]): Cantidad en stock del artículo.
        cantidad (Optional[int]): Cantidad disponible del artículo.
        descontinuado (Optional[int]): Indicador de si el artículo está descontinuado.
    """
    articulo: Optional[str] = Field(None, max_length=15)
    marca: Optional[str] = Field(None, max_length=15)
    modelo: Optional[str] = Field(None, max_length=20)
    departamento_numero: Optional[str] = Field(None, max_length=1)
    clase_numero: Optional[str] = Field(None, max_length=2)
    familia_numero: Optional[str] = Field(None, max_length=3)
    stock: Optional[int] = Field(None, le=999999999)
    cantidad: Optional[int] = Field(None, le=999999999)
    descontinuado: Optional[int] = Field(None, le=1)

class ArticuloInDB(ArticuloBase):
    """
    Modelo que representa un artículo almacenado en la base de datos.

    Attributes:
        fecha_alta (date): Fecha de alta del artículo.
        descontinuado (int): Indicador de si el artículo está descontinuado.
        fecha_baja (date): Fecha de baja del artículo.
    """
    fecha_alta: date
    descontinuado: int
    fecha_baja: date

    class Config:
        orm_mode = True

class DepartamentoSchema(BaseModel):
    """
    Esquema para el modelo de Departamento.

    Attributes:
        numero (str): Número de identificación del departamento.
        nombre (str): Nombre del departamento.
    """
    numero: str
    nombre: str

class FamiliaSchema(BaseModel):
    """
    Esquema para el modelo de Familia.

    Attributes:
        numero (str): Número de identificación de la familia.
        nombre (str): Nombre de la familia.
        departamento_numero (str): Número de identificación del departamento al que pertenece la familia.
        clase_numero (str): Número de identificación de la clase a la que pertenece la familia.
    """
    numero: str
    nombre: str
    departamento_numero: str
    clase_numero: str
