# 🌐 Frontier Forge - Mode Multijoueur Coopératif

## 🚀 Démarrage Rapide

### Joueur Hôte (celui qui héberge la partie)

1. **Lancer Hamachi** et créer un réseau
2. **Démarrer le serveur** :
   ```bash
   python start_server.py
   ```
   Port : 5555 (appuyez sur Entrée)

3. **Lancer le jeu** (nouveau terminal) :
   ```bash
   python main_multiplayer.py
   ```
   - IP : `localhost`
   - Port : `5555`

4. **Donner votre IP Hamachi** aux autres joueurs (ex: `25.12.34.56`)

### Autres Joueurs

1. **Rejoindre le réseau Hamachi** de l'hôte
2. **Lancer le jeu** :
   ```bash
   python main_multiplayer.py
   ```
   - IP : **IP Hamachi de l'hôte** (ex: `25.12.34.56`)
   - Port : `5555`

---

## ✨ Fonctionnalités Multijoueur

### Mode Coopération
- **Inventaire partagé** : Toutes les ressources sont communes
- **Bâtiments partagés** : Tous les joueurs peuvent construire
- **Objectif commun** : Construire la fusée ensemble ou survivre 10 jours
- **Ennemis communs** : Les zombies/mutants/loups attaquent tous les joueurs

### Synchronisation en Temps Réel
- ✅ Position des joueurs (10x par seconde)
- ✅ Inventaire partagé
- ✅ Construction de bâtiments
- ✅ Ennemis (spawn, position, mort)
- ✅ Connexion/déconnexion des joueurs

### Interface
- **Joueur local** : Carré vert (vous)
- **Joueurs distants** : Carré cyan avec ID (P1, P2, etc.)
- **Barre de vie** : Au-dessus de chaque joueur
- **ID joueur** : Affiché au-dessus du joueur

---

## 🎮 Conseils de Jeu en Équipe

### Stratégies Recommandées

**Division des Tâches** :
- 👷 Joueur 1 : Récolte métal + construction mines
- 🌾 Joueur 2 : Récolte nourriture + construction fermes
- ⚡ Joueur 3 : Récolte bois/pierre + construction générateurs
- 🔫 Joueur 4 : Défense (tuer zombies) + construction tourelles

**Construction Coordonnée** :
- Construisez tous au même endroit (base commune)
- Créez des murs défensifs autour de la base
- Placez des tourelles aux angles
- Construisez hôpital au centre

**Communication** :
- Utilisez Discord/TeamSpeak pour parler
- Coordonnez les achats de bâtiments coûteux
- Prévenez quand vous récoltez des ressources rares

---

## 🔧 Architecture Technique

### Fichiers Créés

```
ForgeFrontier/
├── network/
│   ├── __init__.py
│   ├── protocol.py        # Protocole de communication JSON
│   ├── server.py           # Serveur de jeu (autorité)
│   └── client.py           # Client réseau
├── main_multiplayer.py     # Version multijoueur du jeu
├── start_server.py         # Script de lancement serveur
├── MULTIPLAYER_GUIDE.md    # Guide détaillé
└── README_MULTIPLAYER.md   # Ce fichier
```

### Protocole Réseau

**Messages JSON** avec types :
- `connect` : Connexion + attribution ID
- `disconnect` : Déconnexion
- `player_update` : Position/stats joueur
- `inventory_update` : Inventaire partagé
- `building_place` : Construction bâtiment
- `enemy_spawn` : Apparition ennemi
- `enemy_death` : Mort ennemi
- `game_state` : État complet (sync initiale)
- `heartbeat` : Keep-alive (5s)

**Port** : 5555 (TCP)
**Protocole** : Socket TCP avec messages JSON délimités par `\n`

### Autorité Serveur

Le serveur est l'**autorité** pour :
- ✅ Attribution des ID joueurs
- ✅ État global du jeu (inventaire, bâtiments, ennemis)
- ✅ Validation des actions (anti-cheat basique)
- ✅ Relayage des messages entre clients

Les clients envoient :
- Position du joueur (0.1s)
- Inventaire après récolte
- Bâtiments construits

---

## 🐛 Résolution de Problèmes

### Le serveur ne démarre pas
```bash
# Vérifier que le port n'est pas utilisé
netstat -ano | findstr :5555

# Changer le port si nécessaire
python start_server.py
> Port : 5556
```

### Les clients ne se connectent pas
1. **Vérifier Hamachi** : Tous sur le même réseau
2. **Vérifier IP** : Utiliser l'IP Hamachi (25.XX.XX.XX)
3. **Pare-feu Windows** :
   ```
   Panneau de configuration > Pare-feu Windows
   > Autoriser une application
   > Ajouter Python
   ```
4. **Tester avec ping** :
   ```bash
   ping 25.12.34.56
   ```

### Lag / Latence
- **Réduire la fréquence d'update** : Modifier `main_multiplayer.py` ligne ~654
  ```python
  if self.last_network_update >= 0.2:  # Au lieu de 0.1
  ```
- **Réduire les ennemis** : Modifier `constants.py`
  ```python
  ZOMBIE_SPAWN_INTERVAL = 30.0  # Au lieu de 15.0
  ```

### Désynchronisation
- **Redémarrer le serveur** : Arrêter (Ctrl+C) et relancer
- **Tous les clients doivent se reconnecter**
- Le dernier connecté reçoit l'état complet

---

## 📊 Performances

### Consommation Réseau
- **~1 KB/s par joueur** (position + inventaire)
- **Pics à 5-10 KB/s** (spawn ennemis, construction)
- **Total serveur 4 joueurs** : ~20-40 KB/s

### Latence Recommandée
- **< 50ms** : Excellent
- **50-100ms** : Bon (Hamachi typique)
- **100-200ms** : Jouable
- **> 200ms** : Lag visible

---

## 🎯 Limitations Actuelles

### Non Implémenté
- ❌ Sauvegarde multijoueur (désactivée)
- ❌ Chat textuel
- ❌ Lobby de sélection
- ❌ Mode compétitif
- ❌ Spectateurs
- ❌ Reconnexion automatique

### Améliorations Futures (Phase 7C)
- Interpolation de mouvement
- Prédiction côté client
- Compression de données
- Anti-cheat avancé
- Serveur dédié

---

## 💡 Développement

### Tester en Local (sans Hamachi)

**Terminal 1** :
```bash
python start_server.py
> Port : 5555
```

**Terminal 2** :
```bash
python main_multiplayer.py
> IP : localhost
> Port : 5555
```

**Terminal 3** :
```bash
python main_multiplayer.py
> IP : localhost
> Port : 5555
```

### Debug Mode

Dans `network/server.py` et `network/client.py`, décommenter :
```python
# print(f"[DEBUG] Message reçu: {msg_type}")
```

---

**Bon jeu en équipe ! 🚀👥**

_Pour plus de détails, consultez `MULTIPLAYER_GUIDE.md`_
