from motor.motor_asyncio import AsyncIOMotorClient  # Cambia esta importación
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://samuelgvelandia:y4hzzxjfh39APZn3@cluster0.2fkf5oz.mongodb.net/")
DB_NAME = "Lusam"

# Conexión asíncrona
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]

async def verify_connection():
    await client.admin.command("ping")  
