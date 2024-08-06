"""
This module contains CRUD operations for managing articles, departments, classes, and families in the database.
"""

from sqlalchemy.orm import Session
from . import models
from datetime import date

def crear_articulo(db: Session, articulo: models.ArticuloCreate):
    """
    Creates a new article in the database.

    Args:
        db (Session): The database session.
        articulo (models.ArticuloCreate): The article data to create.

    Returns:
        models.Articulo: The created article.

    Raises:
        ValueError: If the quantity is greater than the stock.
    """
    if articulo.cantidad > articulo.stock:
        raise ValueError("La cantidad no puede ser mayor al stock")
    
    db_articulo = models.Articulo(**articulo.dict(), fecha_alta=date.today(), descontinuado=0, fecha_baja=date(1900, 1, 1))
    db.add(db_articulo)
    db.commit()
    db.refresh(db_articulo)
    return db_articulo

def obtener_articulo(db: Session, sku: str):
    """
    Retrieves an article from the database by its SKU.

    Args:
        db (Session): The database session.
        sku (str): The SKU of the article to retrieve.

    Returns:
        models.Articulo: The retrieved article, or None if not found.
    """
    return db.query(models.Articulo).filter(models.Articulo.sku == sku).first()

def actualizar_articulo(db: Session, sku: str, articulo: models.ArticuloUpdate):
    """
    Updates an existing article in the database.

    Args:
        db (Session): The database session.
        sku (str): The SKU of the article to update.
        articulo (models.ArticuloUpdate): The updated article data.

    Returns:
        models.Articulo: The updated article, or None if not found.
    """
    db_articulo = db.query(models.Articulo).filter(models.Articulo.sku == sku).first()
    if db_articulo:
        update_data = articulo.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_articulo, key, value)
        if 'descontinuado' in update_data and update_data['descontinuado'] == 1:
            db_articulo.fecha_baja = date.today()
        db.commit()
        db.refresh(db_articulo)
    return db_articulo

def eliminar_articulo(db: Session, sku: str):
    """
    Deletes an article from the database.

    Args:
        db (Session): The database session.
        sku (str): The SKU of the article to delete.

    Returns:
        models.Articulo: The deleted article, or None if not found.
    """
    db_articulo = db.query(models.Articulo).filter(models.Articulo.sku == sku).first()
    if db_articulo:
        db.delete(db_articulo)
        db.commit()
    return db_articulo

def obtener_departamentos(db: Session):
    """
    Retrieves all departments from the database.

    Args:
        db (Session): The database session.

    Returns:
        List[models.Departamento]: A list of all departments.
    """
    return db.query(models.Departamento).all()

def obtener_clases(db: Session, departamento_numero: str):
    """
    Retrieves all classes for a given department from the database.

    Args:
        db (Session): The database session.
        departamento_numero (str): The department number.

    Returns:
        List[models.Clase]: A list of classes for the given department.
    """
    return db.query(models.Clase).filter(models.Clase.departamento_numero == departamento_numero).all()

def obtener_familias(db: Session, departamento_numero: str, clase_numero: str):
    """
    Retrieves all families for a given department and class from the database.

    Args:
        db (Session): The database session.
        departamento_numero (str): The department number.
        clase_numero (str): The class number.

    Returns:
        List[models.Familia]: A list of families for the given department and class.
    """
    return db.query(models.Familia).filter(models.Familia.departamento_numero == departamento_numero, models.Familia.clase_numero == clase_numero).all()

def cargar_datos(db: Session):
    """
    Loads initial data into the database from a JSON file.

    This function checks if data already exists in the database before loading.
    It loads departments, classes, and families from the JSON file.

    Args:
        db (Session): The database session.

    Raises:
        Exception: If there's an error while loading the data.
    """
    import json
    from . import models

    # Check if data already exists in the database
    if db.query(models.Departamento).first():
        print("Los datos ya están cargados en la base de datos.")
        return

    with open("datos.json", "r") as f:
        datos = json.load(f)

    # Load departments
    for departamento in datos["departamentos"]:
        db_departamento = models.Departamento(numero=departamento["numero"], nombre=departamento["nombre"])
        db.add(db_departamento)

    # Load classes
    for i, clase in enumerate(datos["clases"]):
        departamento_numero = "1" if i < 2 else "2"
        clase_numero = f"{departamento_numero}{clase['numero']}"
        db_clase = models.Clase(numero=clase_numero, nombre=clase["nombre"], departamento_numero=departamento_numero)
        db.add(db_clase)

    # Load families
    for i, departamento_familias in enumerate(datos["familias"]):
        departamento_numero = str(i + 1)
        for clase_numero, familias in departamento_familias.items():
            clase_numero_completo = f"{departamento_numero}{clase_numero}"
            for familia in familias:
                db_familia = models.Familia(
                    numero=familia["numero"], 
                    nombre=familia["nombre"], 
                    departamento_numero=departamento_numero,
                    clase_numero=clase_numero_completo
                )
                db.add(db_familia)

    try:
        db.commit()
        print("Datos cargados exitosamente en la base de datos.")
    except Exception as e:
        db.rollback()
        print(f"Error al cargar los datos: {str(e)}")
        raise