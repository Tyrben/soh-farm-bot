
import pygetwindow as gw
import pyautogui
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WindowManager:
    def __init__(self, window_title="Scars"):
        self.window_title = window_title
        self.window = None
        
    def find_window(self):
        """Cherche la fenêtre contenant 'Scars' dans son titre"""
        windows = gw.getWindowsWithTitle(self.window_title)
        if windows:
            self.window = windows[0]
            logger.info(f"Fenêtre trouvée : {self.window.title}")
            return True
        logger.warning(f"Aucune fenêtre avec '{self.window_title}' trouvée")
        return False
    
    def activate_window(self):
        """Active et met au premier plan la fenêtre"""
        if self.window:
            if self.window.isMinimized:
                self.window.restore()
            self.window.activate()
            logger.info("Fenêtre activée")
            return True
        return False
    
    def get_window_region(self):
        """Retourne la région (x, y, largeur, hauteur) de la fenêtre"""
        if self.window:
            return (self.window.left, self.window.top, 
                   self.window.width, self.window.height)
        return None

