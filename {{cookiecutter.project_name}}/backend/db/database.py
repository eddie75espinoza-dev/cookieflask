from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


db = SQLAlchemy()


def test_connection():
    """
    Método auxiliar para probar la conexión a la base de datos.
    """
    try:
        db.session.execute(text("SELECT 1"))
        return True
    
    except Exception as e:
        return False, str(e)