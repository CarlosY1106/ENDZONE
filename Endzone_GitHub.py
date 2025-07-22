# Segmento 1: Inicialización de Pygame, Configuración de Pantalla y Carga de Activos Básicos

# Este segmento inicializa Pygame, configura la pantalla principal y carga los activos visuales y de audio esenciales
# como la música de fondo, efectos de sonido y las imágenes base del personaje, zombies y proyectiles.
# También define colores y fuentes usadas en la interfaz.

import pygame
import random
import math
import sys

pygame.init()

pygame.mixer.init()
pygame.mixer.music.load("Sonido.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)

# Cargar efectos de sonido
zombie_spawn_sound = pygame.mixer.Sound("SonidoZombie.mp3")
zombie_spawn_sound.set_volume(0.2)
weapon_shoot_sound = pygame.mixer.Sound("SonidoArma.mp3")
weapon_shoot_sound.set_volume(0.1)


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EndZone")
clock = pygame.time.Clock()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 140, 0)
LIGHT_ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GREEN = (0, 200, 0)
DARK_RED = (150, 0, 0)
DARK_GREEN = (0, 150, 0)

button_font = pygame.font.SysFont("Arial", 25)
info_font = pygame.font.SysFont("Arial", 20)

def cargar_imagen_ruta(ruta, ancho_objetivo, alto_objetivo):
    imagen = pygame.image.load(ruta).convert_alpha()
    original_ancho, original_alto = imagen.get_size()
    ratio = min(ancho_objetivo / original_ancho, alto_objetivo / original_alto)
    nuevo_tamano = (int(original_ancho * ratio), int(original_alto * ratio))
    imagen_redimensionada = pygame.transform.smoothscale(imagen, nuevo_tamano)
    return imagen_redimensionada

# Carga imágenes (todas en la misma carpeta)
personaje_img = cargar_imagen_ruta("Personaje.png", 200, 200)
zombie_imgs = [cargar_imagen_ruta(f"Zombie{i}.png", 80, 80) for i in range(1, 16)]
proyectil_img = cargar_imagen_ruta("Proyectil.png", 20, 20)
proyectil_jefe_img = cargar_imagen_ruta("ProyectilZombie.png", 30, 30)

jefe_imgs = {
    1: cargar_imagen_ruta("JefeFinal1.png", 100, 100),
    2: cargar_imagen_ruta("JefeFinal2.png", 130, 130),
    3: cargar_imagen_ruta("JefeFinal3.png", 150, 150)
}

# Nueva imagen de mancha de sangre
blood_stain_img = cargar_imagen_ruta("Sangre.png", 50, 50) # Tamaño ajustable