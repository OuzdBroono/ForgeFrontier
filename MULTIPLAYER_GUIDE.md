# 🌐 Guide Multijoueur - Frontier Forge

## 🎮 Configuration Hamachi (LogMeIn)

### Prérequis
1. **Télécharger Hamachi** : https://vpn.net/
2. Créer un compte LogMeIn
3. Installer Hamachi sur tous les ordinateurs

### Configuration du Réseau

#### Hôte (celui qui lance le serveur) :
1. Lancer Hamachi
2. Créer un nouveau réseau :
   - Cliquer sur "Créer un nouveau réseau"
   - Nom du réseau : `FrontierForge` (ou autre)
   - Mot de passe : `votre_mot_de_passe`
3. Noter votre **IP Hamachi** (ex: `25.XX.XX.XX`)
4. Donner le nom du réseau et le mot de passe aux amis

#### Clients (les autres joueurs) :
1. Lancer Hamachi
2. Rejoindre le réseau :
   - Cliquer sur "Rejoindre un réseau existant"
   - Entrer le nom du réseau : `FrontierForge`
   - Entrer le mot de passe
3. Vous êtes maintenant connectés au même réseau virtuel !

---

## 🚀 Lancer une Partie Multijoueur

### Étape 1 : Hôte - Lancer le Serveur

```bash
cd ForgeFrontier
python start_server.py
```

ou avec Python 3 :
```bash
python3 start_server.py
```

**Le serveur vous demandera :**
- Port (défaut: 5555) → Appuyez sur Entrée pour utiliser 5555

**Le serveur affichera :**
```
✅ Serveur démarré et en écoute...
📡 IP: 0.0.0.0, Port: 5555
👥 Joueurs max: 4
⏳ En attente de connexions...
```

### Étape 2 : Hôte - Lancer le Jeu

Dans un **nouveau terminal** :
```bash
cd ForgeFrontier
python main_multiplayer.py
```

**Le jeu vous demandera :**
- IP du serveur → Tapez `localhost` ou `127.0.0.1`
- Port → Tapez `5555`

### Étape 3 : Clients - Rejoindre la Partie

Sur les autres ordinateurs :
```bash
cd ForgeFrontier
python main_multiplayer.py
```

**Le jeu demandera :**
- IP du serveur → Tapez l'**IP Hamachi de l'hôte** (ex: `25.12.34.56`)
- Port → Tapez `5555`

---

## 🎯 Mode Coopération

### Objectifs Partagés
- **Inventaire commun** : Toutes les ressources sont partagées
- **Bâtiments communs** : Tout le monde peut construire
- **Ennemis communs** : Les ennemis attaquent tous les joueurs
- **Victoire commune** : Construire la fusée ensemble ou survivre 10 jours

### Stratégies Recommandées
1. **Division des tâches** :
   - Joueur 1 : Récolte métal
   - Joueur 2 : Récolte nourriture
   - Joueur 3 : Construction
   - Joueur 4 : Défense (tuer les zombies)

2. **Communication** :
   - Utilisez Discord/TeamSpeak/Skype pour parler
   - Coordonnez vos actions

3. **Base commune** :
   - Construisez tous vos bâtiments au même endroit
   - Créez des murs défensifs autour de la base

---

## 🔧 Dépannage

### Le serveur ne démarre pas
- **Vérifier le port** : Assurez-vous que le port 5555 n'est pas utilisé
- **Pare-feu** : Autorisez Python dans le pare-feu Windows

### Les clients ne peuvent pas se connecter
- **Vérifier Hamachi** : Tous les joueurs doivent être sur le même réseau Hamachi
- **Vérifier l'IP** : Utilisez l'IP Hamachi de l'hôte (25.XX.XX.XX)
- **Vérifier le port** : Doit être 5555 (ou celui choisi par l'hôte)
- **Pare-feu** : Désactiver temporairement ou autoriser le port 5555

### Lag / Latence
- **Hamachi** : Latence normale = 20-100ms
- **Réduire les ennemis** : Modifier `constants.py` pour réduire le spawn
- **Fermer autres apps** : Fermer les téléchargements, streaming, etc.

### Désynchronisation
- **Redémarrer** : Arrêter le serveur et tous les clients, puis relancer
- **Vérifier versions** : Tous les joueurs doivent avoir la même version du jeu

---

## 📊 Commandes Serveur

Dans le terminal du serveur :
- **Ctrl+C** : Arrêter le serveur proprement
- Le serveur affiche les connexions/déconnexions en temps réel

---

## 🎮 Différences Solo vs Multijoueur

| Fonctionnalité | Solo | Multijoueur |
|----------------|------|-------------|
| Inventaire | Personnel | **Partagé** |
| Bâtiments | Individuels | **Communs** |
| Ennemis | Ciblent le joueur | Ciblent tous les joueurs |
| Pause | Possible (ESC) | **Impossible** |
| Sauvegarde | F5/F9 | **Désactivée** |

---

## 💡 Conseils

1. **L'hôte doit avoir une bonne connexion** : Il gère tout le jeu
2. **Restez proches** : Plus facile de se défendre ensemble
3. **Partagez les ressources** : L'inventaire est commun
4. **Construisez ensemble** : 4 joueurs = base 4x plus vite !

---

## 🐛 Rapporter des Bugs

Si vous rencontrez des problèmes :
1. Noter ce qui s'est passé
2. Vérifier la console du serveur (messages d'erreur)
3. Créer un issue sur GitHub

**Bon jeu en équipe ! 🚀**
