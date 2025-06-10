# motor.motor_asyncio es un cliente asíncrono para mongodb
# permite operaciones no bloqueantes con la base de datos, o sea, que si hago una consulta
# pueden haber otras acciones en el sistema mientras la consulta está en proceso
from motor.motor_asyncio import AsyncIOMotorClient
import os

# configuración de la url de conexión a mongodb
# os.getenv busca una variable de entorno llamada "MONGODB_URL"
# si no existe, usa la url por defecto que apunta a un cluster de mongodb atlas
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://samuelgvelandia:y4hzzxjfh39APZn3@cluster0.2fkf5oz.mongodb.net/")
# nombre de la base de datos que se usa en la aplicación
DB_NAME = "Lusam"

# creación de una instancia del cliente asíncrono de mongodb
# este cliente manejará todas las conexiones a la base de datos
client = AsyncIOMotorClient(MONGODB_URL)
# selección de la base de datos específica dentro del cluster
# esto es como decir "usa esta base de datos para todas las operaciones"
db = client[DB_NAME]

# función asíncrona para verificar que la conexión a mongodb está activa
async def verify_connection():
    # hace un ping al servidor de mongodb
    # si la conexión está activa, el comando ping responderá
    # si hay error, lanzará una excepción
    await client.admin.command("ping")  
