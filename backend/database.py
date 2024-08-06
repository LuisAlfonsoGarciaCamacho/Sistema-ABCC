from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de la base de datos SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# Crear motor de base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Crear una fábrica de sesiones con autocommit y autoflush deshabilitados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una clase base para los modelos ORM
Base = declarative_base()

def init_db():
    """
    Inicializa la base de datos, eliminando todas las tablas existentes y 
    creando nuevas tablas según las definiciones de los modelos ORM.

    Esta función debe ser usada con precaución en entornos de producción 
    ya que elimina todos los datos existentes en la base de datos.
    """
    # Eliminar todas las tablas existentes en la base de datos
    Base.metadata.drop_all(bind=engine)
    # Crear todas las tablas definidas en los modelos ORM
    Base.metadata.create_all(bind=engine)
