#!/usr/bin/env python3
"""
Point d'entrée du bot
"""

from bot_core import SoHBot

def main():
    print("\n" + "="*50)
    print("🤖 Scars of Honor Bot - Détection carré jaune")
    print("="*50)
    
    bot = SoHBot()
    
    input("\nAppuyez sur ENTRÉE pour scanner et cliquer...")
    
    if bot.click_once():
        print("\n✅ Succès !")
    else:
        print("\n❌ Échec")
        print("💡 Vérifiez 'debug_last_scan.png'")

if __name__ == "__main__":
    main()
