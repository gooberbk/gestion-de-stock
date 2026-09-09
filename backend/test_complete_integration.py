import asyncio
import websockets
import json
import requests

async def test_complete_integration():
    # 1. Créer un produit de test
    print("📦 Création d'un produit de test...")
    produit_data = {
        "code_qr": "TEST2024",
        "nom": "Produit Test WebSocket",
        "categorie": "Test",
        "prix_achat": 5.0,
        "prix_vente": 10.0,
        "quantite_stock": 20,
        "seuil_alerte": 5,
        "prix_achat_confirme": True
    }
    
    response = requests.post("http://localhost:8000/produits", json=produit_data)
    if response.status_code == 201:
        print("✅ Produit créé avec succès")
        produit = response.json()
        print(f"   ID: {produit['id']}, Nom: {produit['nom']}")
    else:
        print(f"❌ Erreur création produit: {response.status_code}")
        return
    
    # 2. Connecter le WebSocket
    print("\n🔌 Connexion WebSocket...")
    uri = "ws://localhost:8000/ws"
    
    events_received = []
    
    async with websockets.connect(uri) as websocket:
        print("✅ WebSocket connecté")
        
        # Message de bienvenue
        welcome_msg = await websocket.recv()
        print(f"   Message de bienvenue: {json.loads(welcome_msg)['message']}")
        
        # 3. Effectuer une vente
        print("\n💰 Enregistrement d'une vente...")
        vente_data = {
            "code_qr": "TEST2024",
            "quantite_vendue": 3,
            "prix_vente_override": 12.0
        }
        
        vente_response = requests.post("http://localhost:8000/ventes", json=vente_data)
        if vente_response.status_code == 201:
            vente = vente_response.json()
            print(f"✅ Vente enregistrée: {vente['produit_nom']}, Qté: {vente['quantite_vendue']}")
            print(f"   Marge: {vente['marge_totale']}€, Stock après: {vente['stock_apres_vente']}")
        else:
            print(f"❌ Erreur vente: {vente_response.status_code}")
            return
        
        # 4. Écouter les événements WebSocket
        print("\n📡 Écoute des événements WebSocket...")
        try:
            # Timeout de 5 secondes pour recevoir les événements
            for i in range(2):  # On attend 2 événements (vente + marge_du_jour)
                event = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                event_data = json.loads(event)
                events_received.append(event_data)
                print(f"   Événement reçu: {event_data['type']}")
                
                if event_data['type'] == 'vente':
                    print(f"      Produit: {event_data['produit_nom']}")
                    print(f"      Nouveau stock: {event_data['nouveau_stock']}")
                    print(f"      Marge: {event_data['marge']}€")
                elif event_data['type'] == 'marge_du_jour':
                    print(f"      CA du jour: {event_data['total_ca']}€")
                    print(f"      Marge du jour: {event_data['total_marge']}€")
                    print(f"      Nombre ventes: {event_data['nombre_ventes']}")
                    
        except asyncio.TimeoutError:
            print("⏱️  Timeout: Plus d'événements reçus")
        
        # 5. Vérifier les endpoints REST
        print("\n📊 Vérification des endpoints REST...")
        
        # Statistiques du jour
        stats_response = requests.get("http://localhost:8000/statistiques/jour")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print("✅ GET /statistiques/jour")
            print(f"   CA: {stats['total_ca']}€, Marge: {stats['total_marge']}€")
            print(f"   Dernières ventes: {len(stats['dernieres_ventes'])}")
        
        # Transactions
        trans_response = requests.get("http://localhost:8000/transactions?limite=5")
        if trans_response.status_code == 200:
            trans = trans_response.json()
            print("✅ GET /transactions?limite=5")
            print(f"   Total transactions: {trans['total']}")
    
    print("\n🎉 Test d'intégration terminé avec succès !")
    print(f"   Événements WebSocket reçus: {len(events_received)}")
    
    # Nettoyage
    print("\n🧹 Nettoyage...")
    delete_response = requests.delete(f"http://localhost:8000/produits/{produit['id']}")
    if delete_response.status_code == 204:
        print("✅ Produit de test supprimé")

if __name__ == "__main__":
    asyncio.run(test_complete_integration())