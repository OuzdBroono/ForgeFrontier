#!/bin/bash
# Script de test rapide pour le multijoueur
# Usage: ./test_multiplayer.sh [server|client]

cd "/mnt/c/Users/ouzdi/Desktop/Frontier Forge/ForgeFrontier"

case "$1" in
    server)
        echo "🎮 Démarrage du serveur..."
        echo ""
        echo "Port par défaut : 5555"
        echo "Appuyez sur Entrée pour utiliser le port par défaut"
        echo ""
        python3 start_server.py
        ;;
    client)
        echo "🎮 Démarrage du client multijoueur..."
        echo ""
        echo "Pour test local :"
        echo "  IP: localhost"
        echo "  Port: 5555"
        echo ""
        python3 main_multiplayer.py
        ;;
    *)
        echo "Usage: $0 [server|client]"
        echo ""
        echo "Ouvrez 3 terminaux :"
        echo "  Terminal 1: ./test_multiplayer.sh server"
        echo "  Terminal 2: ./test_multiplayer.sh client"
        echo "  Terminal 3: ./test_multiplayer.sh client"
        exit 1
        ;;
esac
