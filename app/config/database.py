from motor.motor_asyncio import AsyncIOMotorClient  # Cambia esta importación
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = "Lusam"

# Conexión asíncrona
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]

async def verify_connection():
    await client.admin.command("ping")  