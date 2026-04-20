#!/usr/bin/env python3
"""
Cœur du bot - Détection et clics (Linux & Windows)
"""

import cv2
import numpy as np
import pyautogui
import time
import logging
import sys
import platform

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Détection du système d'exploitation
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

if IS_WINDOWS:
    import pydirectinput  # Windows uniquement
    INPUT_LIB = pydirectinput
    logger.info("🐍 Mode Windows - Utilisation de pydirectinput")
else:
    # Sur Linux, pyautogui fonctionne bien
    INPUT_LIB = pyautogui
    logger.info("🐧 Mode Linux - Utilisation de pyautogui")


class ScarsBot:
    def __init__(self):
        self.window_id = None
        self.window_title = "Scars"
        self.use_xdotool = IS_LINUX  # xdotool uniquement sur Linux
    
    def find_window_linux(self):
        """Trouve la fenêtre du jeu sous Linux avec xdotool"""
        import subprocess
        
        try:
            result = subprocess.run(
                ['xdotool', 'search', '--name', self.window_title],
                capture_output=True, text=True
            )
            windows = result.stdout.strip().split('\n')
            if windows and windows[0]:
                self.window_id = windows[0]
                logger.info(f"✅ Fenêtre trouvée (ID: {self.window_id})")
                return True
            logger.warning(f"❌ Fenêtre '{self.window_title}' non trouvée")
            return False
        except FileNotFoundError:
            logger.error("xdotool non installé. Installez-le avec: sudo apt install xdotool")
            return False
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return False
    
    def find_window_windows(self):
        """Trouve la fenêtre du jeu sous Windows avec pygetwindow"""
        import pygetwindow as gw
        
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if windows:
                self.window = windows[0]
                logger.info(f"✅ Fenêtre trouvée: {self.window.title}")
                return True
            logger.warning(f"❌ Fenêtre '{self.window_title}' non trouvée")
            return False
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return False
    
    def find_window(self):
        """Trouve la fenêtre selon l'OS"""
        if IS_LINUX:
            return self.find_window_linux()
        else:
            return self.find_window_windows()
    
    def get_window_region_linux(self):
        """Récupère la région sous Linux"""
        import subprocess
        
        try:
            result = subprocess.run(
                ['xdotool', 'getwindowgeometry', self.window_id],
                capture_output=True, text=True
            )
            lines = result.stdout.strip().split('\n')
            position = lines[1].split(':')[1].strip().split(',')
            geometry = lines[2].split(':')[1].strip().split('x')
            
            x, y = int(position[0]), int(position[1])
            w, h = int(geometry[0]), int(geometry[1])
            
            logger.info(f"Région: ({x}, {y}) -> {w}x{h}")
            return (x, y, w, h)
        except Exception as e:
            logger.error(f"Erreur région: {e}")
            return None
    
    def get_window_region_windows(self):
        """Récupère la région sous Windows"""
        try:
            x, y = self.window.left, self.window.top
            w, h = self.window.width, self.window.height
            logger.info(f"Région: ({x}, {y}) -> {w}x{h}")
            return (x, y, w, h)
        except Exception as e:
            logger.error(f"Erreur région: {e}")
            return None
    
    def get_window_region(self):
        """Récupère la région selon l'OS"""
        if IS_LINUX:
            return self.get_window_region_linux()
        else:
            return self.get_window_region_windows()
    
    def activate_window_linux(self):
        """Active la fenêtre sous Linux"""
        import subprocess
        try:
            subprocess.run(['xdotool', 'windowactivate', self.window_id])
            time.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"Erreur activation: {e}")
            return False
    
    def activate_window_windows(self):
        """Active la fenêtre sous Windows"""
        try:
            self.window.activate()
            time.sleep(0.3)
            return True
        except Exception as e:
            logger.error(f"Erreur activation: {e}")
            return False
    
    def activate_window(self):
        """Active la fenêtre selon l'OS"""
        if IS_LINUX:
            return self.activate_window_linux()
        else:
            return self.activate_window_windows()
    
    def detect_yellow_square(self, image, target_size=64):
        """Détecte un carré jaune dans l'image (identique pour tous les OS)"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Plage de jaune
        lower = np.array([20, 100, 100])
        upper = np.array([30, 255, 255])
        
        mask = cv2.inRange(hsv, lower, upper)
        
        # Nettoyage
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Vérifier si c'est un carré de taille ~64px
            if 0.8 <= w/h <= 1.2 and (target_size - 30) <= w <= (target_size + 30):
                center = (x + w//2, y + h//2)
                logger.info(f"🎯 Carré trouvé: {w}x{h}px au centre {center}")
                return center
        return None
    
    def click(self, x, y):
        """Clic multiplateforme"""
        INPUT_LIB.moveTo(x, y)
        INPUT_LIB.click()
        logger.info(f"🖱️ Clic à ({x}, {y})")
    
    def click_once(self):
        """Exécute une détection et un clic unique"""
        if not self.find_window():
            return False
        
        if not self.activate_window():
            logger.warning("Impossible d'activer la fenêtre, tentative quand même...")
        
        region = self.get_window_region()
        if not region:
            return False
        
        # Capturer l'écran
        screenshot = pyautogui.screenshot(region=region)
        image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        cv2.imwrite("debug_last_scan.png", image)
        
        pos = self.detect_yellow_square(image)
        
        if pos:
            screen_x = region[0] + pos[0]
            screen_y = region[1] + pos[1]
            self.click(screen_x, screen_y)
            return True
        else:
            logger.warning("❌ Aucun carré jaune détecté")
            return False

