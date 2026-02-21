#!/usr/bin/env python3
"""
Script de lancement du serveur multijoueur
"""

import sys
import os

# Ajouter le dossier network au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'network'))

from network.server import GameServer

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 FRONTIER FORGE - SERVEUR MULTIJOUEUR")
    print("=" * 60)
    print()
    print("📋 Instructions:")
    print("  1. Le serveur va démarrer sur toutes les interfaces (0.0.0.0)")
    print("  2. Les joueurs pourront se connecter via Hamachi")
    print("  3. Donnez votre IP Hamachi aux joueurs")
    print()

    # Demander le port
    try:
        port_input = input("Port du serveur (défaut: 5555): ").strip()
        port = int(port_input) if port_input else 5555
    except:
        port = 5555

    max_players = 4  # Maximum 4 joueurs

    print()
    print("🚀 Démarrage du serveur...")
    print()

    server = GameServer(host='0.0.0.0', port=port, max_players=max_players)
    server.start()
