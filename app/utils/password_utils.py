import bcrypt

def hash_password(password: str) -> str:
    """
    Genera un hash seguro de la contraseña usando bcrypt.
    
    Args:
        password (str): La contraseña en texto plano
        
    Returns:
        str: El hash de la contraseña
    """
    # Convertir la contraseña a bytes
    password_bytes = password.encode('utf-8')
    
    # Generar el salt y el hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Devolver el hash como string
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash.
    
    Args:
        plain_password (str): La contraseña en texto plano a verificar
        hashed_password (str): El hash almacenado de la contraseña
        
    Returns:
        bool: True si la contraseña coincide, False en caso contrario
    """
    # Convertir las contraseñas a bytes
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    
    # Verificar la contraseña
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes) 