#!/usr/bin/env python3
"""
Test d'intégration WebSocket pour valider le temps réel.
Ce script :
1. Se connecte au WebSocket
2. Déclenche une vente via POST /ventes
3. Vérifie que le message est bien poussé en temps réel via le WebSocket
"""

import asyncio
import websockets
import requests
import json
from datetime import datetime

# Configuration
WS_URL = "ws://localhost:8000/ws"
API_URL = "http://localhost:8000"
TEST_PRODUCT_QR = "TEST001"

async def test_websocket_integration():
    print("=== Test d'intégration WebSocket ===")
    print(f"WebSocket URL: {WS_URL}")
    print(f"API URL: {API_URL}")
    print()
    
    # Messages reçus via WebSocket
    ws_messages = []
    
    async with websockets.connect(WS_URL) as websocket:
        print("✅ Connecté au WebSocket")
        
        # Écouter les messages en arrière-plan
        async def listen_messages():
            try:
                async for message in websocket:
                    data = json.loads(message)
                    ws_messages.append(data)
                    print(f"📨 Message WebSocket reçu: {data.get('type', 'unknown')}")
                    if data.get('type') == 'connection':
                        print(f"   Clients connectés: {data.get('clients_connectes')}")
            except websockets.exceptions.ConnectionClosed:
                print("❌ WebSocket fermé")
        
        # Démarrer l'écoute en arrière-plan
        listen_task = asyncio.create_task(listen_messages())
        
        # Attendre un peu pour que la connexion soit établie
        await asyncio.sleep(1)
        
        # Déclencher une vente via POST /ventes
        print(f"\n🛒 Création d'une vente pour le produit {TEST_PRODUCT_QR}...")
        vente_payload = {
            "code_qr": TEST_PRODUCT_QR,
            "quantite_vendue": 1
        }
        
        try:
            response = requests.post(f"{API_URL}/ventes", json=vente_payload)
            if response.status_code == 201:
                vente_data = response.json()
                print(f"✅ Vente créée avec succès")
                print(f"   Transaction ID: {vente_data.get('transaction_id')}")
                print(f"   Produit: {vente_data.get('produit_nom')}")
                print(f"   Marge: {vente_data.get('marge_totale')} DA")
            else:
                print(f"❌ Erreur création vente: {response.status_code}")
                print(f"   {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erreur requête API: {e}")
            return False
        
        # Attendre les messages WebSocket
        print("\n⏳ Attente des messages WebSocket (5 secondes)...")
        await asyncio.sleep(5)
        
        # Arrêter l'écoute
        listen_task.cancel()
        try:
            await listen_task
        except asyncio.CancelledError:
            pass
        
        # Analyser les résultats
        print(f"\n📊 Analyse des résultats:")
        print(f"   Messages reçus: {len(ws_messages)}")
        
        # Vérifier les types de messages attendus
        vente_messages = [m for m in ws_messages if m.get('type') == 'vente']
        marge_messages = [m for m in ws_messages if m.get('type') == 'marge_du_jour']
        connection_messages = [m for m in ws_messages if m.get('type') == 'connection']
        
        print(f"   Messages 'connection': {len(connection_messages)}")
        print(f"   Messages 'vente': {len(vente_messages)}")
        print(f"   Messages 'marge_du_jour': {len(marge_messages)}")
        
        # Validation
        success = True
        
        if not connection_messages:
            print("❌ Aucun message de connexion reçu")
            success = False
        else:
            print("✅ Message de connexion reçu")
        
        if not vente_messages:
            print("❌ Aucun message 'vente' reçu après la création de vente")
            success = False
        else:
            print("✅ Message 'vente' reçu")
            vente_msg = vente_messages[0]
            print(f"   Produit: {vente_msg.get('produit_nom')}")
            print(f"   Quantité: {vente_msg.get('quantite_vendue')}")
            print(f"   Nouveau stock: {vente_msg.get('nouveau_stock')}")
        
        if not marge_messages:
            print("⚠️  Aucun message 'marge_du_jour' reçu (peut être normal si pas de ventes du jour)")
        else:
            print("✅ Message 'marge_du_jour' reçu")
            marge_msg = marge_messages[0]
            print(f"   Marge totale: {marge_msg.get('total_marge')} DA")
            print(f"   CA: {marge_msg.get('total_ca')} DA")
        
        print("\n" + "="*50)
        if success:
            print("✅ TEST RÉUSSI: Le WebSocket fonctionne correctement")
        else:
            print("❌ TEST ÉCHOUÉ: Le WebSocket ne fonctionne pas correctement")
        print("="*50)
        
        return success

if __name__ == "__main__":
    try:
        result = asyncio.run(test_websocket_integration())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu")
        exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
