# Audit de Sécurité - Gestion de Stock

## Date de l'audit
14 septembre 2026

## Contexte
Audit de sécurité effectué pour le pilote en réseau local fermé (pas encore en production publique).

## Risques identifiés

### 🔴 Critiques

| Aspect | État actuel | Risque | Recommandation |
|--------|-------------|--------|----------------|
| **Authentification** | ❌ Aucune authentification | N'importe qui sur le réseau peut accéder à l'API et modifier les données | Implémenter une authentification (clé API ou JWT) avant déploiement public |
| **WebSocket** | ❌ Pas d'authentification | N'importe qui peut se connecter au WebSocket et recevoir les données en temps réel | Ajouter une authentification sur la connexion WebSocket |

### 🟡 Moyens

| Aspect | État actuel | Risque | Recommandation |
|--------|-------------|--------|----------------|
| **Exposition API** | ⚠️ Écoute sur `0.0.0.0:8000` | Accessible depuis toutes les interfaces réseau | Restreindre à localhost ou IP spécifique si possible |
| **CORS** | ⚠️ `allow_origins=["*"]` | Accepte les requêtes de n'importe quelle origine | Restreindre aux domaines autorisés après le pilote |

### 🟢 Acceptables pour le pilote

| Aspect | État actuel | Commentaire |
|--------|-------------|-------------|
| **Validation inputs** | ✅ Pydantic avec contraintes | Protection contre les données invalides |
| **SQL Injection** | ✅ Requêtes paramétrées | Protection contre injection SQL |
| **Transactions** | ✅ Atomicité garantie | Protection contre les incohérences |

## Mesures prises pour le pilote

Pour le MVP pré-pilote en réseau local fermé :

1. **Documentation des risques** : Ce document identifie clairement les risques
2. **Réseau local fermé** : L'application ne sera utilisée que sur un réseau WiFi privé
3. **Backup automatique** : Système de sauvegarde implémenté pour protéger les données
4. **Surveillance** : Le commerçant contrôle physiquement l'accès au réseau

## Recommandations pour le futur

### Avant déploiement public

1. **Implémenter une authentification robuste** :
   - Option A : Clé API simple (pour MVP)
   - Option B : JWT avec refresh tokens (pour production)
   - Option C : OAuth2 (pour intégration avec d'autres systèmes)

2. **Restreindre CORS** :
   - Remplacer `allow_origins=["*"]` par la liste des domaines autorisés
   - Exemple : `allow_origins=["https://monapp.com", "http://localhost:3000"]`

3. **Sécuriser WebSocket** :
   - Ajouter une authentification lors de la connexion
   - Valider le token dans le handshake WebSocket

4. **HTTPS/TLS** :
   - Utiliser HTTPS pour toutes les communications
   - Certificats SSL/TLS valides

5. **Rate limiting** :
   - Limiter le nombre de requêtes par IP
   - Protéger contre les attaques DDoS

### Pour le pilote (réseau local)

1. **Changer la clé par défaut** : Si une authentification est ajoutée, utiliser une clé forte
2. **Surveillance réseau** : Vérifier régulièrement les appareils connectés
3. **Backup régulier** : Maintenir le système de sauvegarde automatique
4. **Journalisation** : Ajouter des logs pour tracer les accès

## Conclusion

Pour le pilote en réseau local fermé, les risques actuels sont **acceptables** car :
- Le réseau est contrôlé par le commerçant
- L'accès physique est limité
- Des backups automatiques sont en place
- L'objectif est de valider le concept, pas de sécuriser une production publique

Cependant, **une authentification devra être implémentée** avant tout déploiement public ou utilisation sur un réseau non contrôlé.
