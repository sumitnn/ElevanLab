import os
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
from dotenv import load_dotenv
from contextlib import asynccontextmanager
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

if not MONGO_URI or not MONGO_DB_NAME:
    raise ValueError("MONGO_URI and MONGO_DB_NAME must be set in environment variables")

# ✅ Single global client
client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=3000)
db = client[MONGO_DB_NAME]

async def get_db():
    try:
        # Test connection (ping)
        await db.command("ping")
        return db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection failed: {str(e)}")





@asynccontextmanager
async def lifespan(app): 
    try:
        # Test connection on startup
        await  db.command("ping")
        print(" ✅ MongoDB connected successfully")
        yield 
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise e
    finally:
        client.close()
        print("🛑 MongoDB connection closed")