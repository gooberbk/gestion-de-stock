import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connecté au WebSocket")
            
            # Message de bienvenue
            message = await websocket.recv()
            print(f"Message reçu: {message}")
            
            # Envoyer un message de test
            await websocket.send("ping")
            response = await websocket.recv()
            print(f"Réponse: {response}")
            
            print("✅ Test WebSocket réussi")
            
    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())