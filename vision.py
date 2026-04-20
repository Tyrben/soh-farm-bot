import cv2
import numpy as np
import pyautogui
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class VisionDetector:
    def __init__(self, target_color=(0, 255, 255), tolerance=30):
        """
        target_color: BGR - (0, 255, 255) = jaune
        tolerance: tolérance de couleur (0-255)
        """
        self.target_color = target_color
        self.tolerance = tolerance
        
    def capture_screen_region(self, region):
        """Capture une région spécifique de l'écran"""
        screenshot = pyautogui.screenshot(region=region)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    def detect_yellow_square(self, image, square_size=64):
        """
        Détecte un carré jaune de taille square_size x square_size
        Retourne les coordonnées (x, y) du centre si trouvé
        """
        # Convertir en HSV pour meilleure détection de couleur
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Définir la plage de jaune en HSV
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        
        # Masque pour la couleur jaune
        mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        
        # Nettoyer le masque
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        # Trouver les contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Obtenir le rectangle englobant
            x, y, w, h = cv2.boundingRect(contour)
            
            # Vérifier si c'est un carré (approx) de la bonne taille
            if abs(w - h) <= 10 and square_size - 20 <= w <= square_size + 20:
                center_x = x + w // 2
                center_y = y + h // 2
                logger.info(f"Carré jaune détecté à ({center_x}, {center_y})")
                return (center_x, center_y)
        
        logger.debug("Aucun carré jaune trouvé")
        return None
    
    def debug_save_detection(self, image, mask, filename="debug_detection.png"):
        """Sauvegarde l'image et le masque pour déboguer"""
        h, w = image.shape[:2]
        debug_img = np.hstack([image, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)])
        cv2.imwrite(filename, debug_img)
        logger.info(f"Image de debug sauvegardée : {filename}")

