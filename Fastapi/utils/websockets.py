

import asyncio
import json
import websockets
import threading
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from typing import Dict
load_dotenv()


mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=3000)
db = mongo_client["userAppointment"]


COLLECTION_NAME="practitioners"
AGENT_ID = "IMa5Xl08LSeUuaMyITPj"
# AGENT_ID = "9BuUyTBtF1zuhDwZc8pB"
ELEVENLAB_WS_URL = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={AGENT_ID}"

# WebSocket connection registry per conversation
connections: Dict[str, dict] = {}


# Function to send data to a specific ElevenLabs conversation
async def send_to_elevenlabs(conversation_id: str, data: dict):
    conn = connections.get(conversation_id)
    if not conn or not conn["thread"].is_alive():
        raise RuntimeError(f"WebSocket for conversation {conversation_id} is not running")

    await conn["ready"].wait()
    await conn["queue"].put(data)
    print(f"📤 Sent data to {conversation_id}: ")


# Handle received messages from ElevenLabs
async def handle_received_message(message: str, conversation_id: str):
    print(f"[{conversation_id}] ")
    try:
        parsed = json.loads(message)
        print(f"[{conversation_id}] ")

        if parsed.get("type") == "conversation_initiation_metadata":
            db_response = await db["practitioners"].find({"active": True}).to_list(length=50)
            practitioners = [
                {
                    "practitioner_id": doc.get("user", {}).get("id"),
                    "practitioner_name": f"{doc.get('user', {}).get('first_name', '')} {doc.get('user', {}).get('last_name', '')}".strip()
                }
                for doc in db_response
            ]

            await send_to_elevenlabs(conversation_id, {
                "text": "Available practitioners data", 
                "conversation_id": conversation_id,
                "text": practitioners,
            })

    except Exception as e:
        print(f"[{conversation_id}] ")


# WebSocket connection handler for a single conversation
async def websocket_handler(conversation_id: str):
    conn = connections[conversation_id]
    try:
        async with websockets.connect(ELEVENLAB_WS_URL) as ws:
            conn["ws"] = ws
            conn["ready"].set()
            print(f"✅ [{conversation_id}] Connected to ElevenLabs")

            while not conn["stop"].is_set():
                # Send messages
                try:
                    data = await asyncio.wait_for(conn["queue"].get(), timeout=1.0)
                    await ws.send(json.dumps(data))
                    print(f"📤 [{conversation_id}] ")
                except asyncio.TimeoutError:
                    pass

                # Receive messages
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    await handle_received_message(message, conversation_id)
                except asyncio.TimeoutError:
                    pass

    except Exception as e:
        print(f"❌ [{conversation_id}] WebSocket error: {e}")
    finally:
        conn["ready"].clear()
        conn["ws"] = None
        print(f"🔌 [{conversation_id}] WebSocket closed.")


# Run a WebSocket connection in a thread
def run_websocket_thread(conversation_id: str):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(websocket_handler(conversation_id))


# Start WebSocket connection for a conversation
def start_websocket(conversation_id: str):
    if conversation_id in connections and connections[conversation_id]["thread"].is_alive():
        raise RuntimeError(f"WebSocket for conversation {conversation_id} already running")

    print(f"🚀 Starting WebSocket for conversation {conversation_id}")
    loop_ready = asyncio.Event()
    queue = asyncio.Queue()
    stop_event = asyncio.Event()
    thread = threading.Thread(target=run_websocket_thread, args=(conversation_id,), daemon=True)

    connections[conversation_id] = {
        "ws": None,
        "ready": loop_ready,
        "queue": queue,
        "stop": stop_event,
        "thread": thread,
    }

    thread.start()
    loop_ready.wait()  # Block until ready
    print(f"✅ WebSocket ready for conversation {conversation_id}")


# Stop WebSocket connection for a conversation
def stop_websocket(conversation_id: str):
    conn = connections.get(conversation_id)
    if not conn or not conn["thread"].is_alive():
        raise RuntimeError(f"No active WebSocket for conversation {conversation_id}")

    conn["stop"].set()
    conn["thread"].join(timeout=5)
    conn["ready"].clear()
    print(f"🛑 Stopped WebSocket for conversation {conversation_id}")
    del connections[conversation_id]