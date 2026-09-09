import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connecté au WebSocket")
            
            # Message de bienvenue
            message = await websocket.recv()
            data = json.loads(message)
            print(f"✓ Message de bienvenue: {data}")
            
            # Envoyer un message test
            await websocket.send("test")
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✓ Réponse echo: {data}")
            
            print("✓ Test WebSocket réussi")
            
    except Exception as e:
        print(f"✗ Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
