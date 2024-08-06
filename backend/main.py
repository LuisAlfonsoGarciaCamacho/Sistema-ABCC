from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import crud, models, database
from .database import SessionLocal, engine, init_db

# Create all tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    """
    Dependency to get a database session.

    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    """
    Initializes the database and loads initial data when the application starts.
    """
    init_db()
    db = SessionLocal()
    crud.cargar_datos(db)
    db.close()

@app.post("/articulos/")
def crear_articulo(articulo: models.ArticuloCreate, db: Session = Depends(get_db)):
    """
    Creates a new article.

    Args:
        articulo (models.ArticuloCreate): The article data to create.
        db (Session): The database session.

    Returns:
        dict: The created article data.

    Raises:
        HTTPException: If there's an error creating the article.
    """
    try:
        return crud.crear_articulo(db, articulo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/articulos/{sku}")
def obtener_articulo(sku: str, db: Session = Depends(get_db)):
    """
    Retrieves an article by its SKU.

    Args:
        sku (str): The SKU of the article to retrieve.
        db (Session): The database session.

    Returns:
        dict: The article data.

    Raises:
        HTTPException: If the article is not found.
    """
    articulo = crud.obtener_articulo(db, sku)
    if articulo is None:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return articulo

@app.put("/articulos/{sku}")
def actualizar_articulo(sku: str, articulo: models.ArticuloUpdate, db: Session = Depends(get_db)):
    """
    Updates an existing article.

    Args:
        sku (str): The SKU of the article to update.
        articulo (models.ArticuloUpdate): The updated article data.
        db (Session): The database session.

    Returns:
        dict: The updated article data.
    """
    return crud.actualizar_articulo(db, sku, articulo)

@app.delete("/articulos/{sku}")
def eliminar_articulo(sku: str, db: Session = Depends(get_db)):
    """
    Deletes an article.

    Args:
        sku (str): The SKU of the article to delete.
        db (Session): The database session.

    Returns:
        dict: A message confirming the deletion.
    """
    return crud.eliminar_articulo(db, sku)

@app.get("/departamentos/")
def obtener_departamentos(db: Session = Depends(get_db)):
    """
    Retrieves all departments.

    Args:
        db (Session): The database session.

    Returns:
        list: A list of all departments.
    """
    return crud.obtener_departamentos(db)

@app.get("/clases/{departamento_numero}")
def obtener_clases(departamento_numero: str, db: Session = Depends(get_db)):
    """
    Retrieves all classes for a given department.

    Args:
        departamento_numero (str): The department number.
        db (Session): The database session.

    Returns:
        list: A list of classes for the given department.

    Raises:
        HTTPException: If no classes are found for the department.
    """
    clases = crud.obtener_clases(db, departamento_numero)
    if not clases:
        raise HTTPException(status_code=404, detail=f"No se encontraron clases para el departamento {departamento_numero}")
    return clases

@app.get("/familias/{departamento_numero}/{clase_numero}")
def obtener_familias(departamento_numero: str, clase_numero: str, db: Session = Depends(get_db)):
    """
    Retrieves all families for a given department and class.

    Args:
        departamento_numero (str): The department number.
        clase_numero (str): The class number.
        db (Session): The database session.

    Returns:
        list: A list of families for the given department and class.
    """
    return crud.obtener_familias(db, departamento_numero, clase_numero)