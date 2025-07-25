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
blood_stain_img = cargar_imagen_ruta("Sangre.png", 50, 50)

# Segmento 2: Estructura del Menú Principal y Funciones de Utilidad de UI

# Este segmento define las variables de estado del juego para el menú y las instrucciones,
# así como el logotipo del menú y las partículas de "brasas" para el fondo.
# Incluye las funciones para dibujar botones y barras de salud personalizadas,
# elementos clave para la interacción del usuario.

show_menu = True
run_game = False
show_instructions = False

# Logotipo para menú
logotipo_img = cargar_imagen_ruta("Logotipo.png", 300, 300)

# Brasas para fondo menú e historia
menu_brasas = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'speed': random.uniform(0.2, 0.6)} for _ in range(60)]

def draw_button(text, x, y, w, h, base_color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    is_hovered = rect.collidepoint(mouse)

    pygame.draw.rect(screen, WHITE, rect, border_radius=10)
    inner_rect = rect.inflate(-4, -4)
    pygame.draw.rect(screen, hover_color if is_hovered else base_color, inner_rect, border_radius=8)

    text_surf = button_font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

    if is_hovered and click[0] == 1 and action:
        pygame.time.wait(150)
        action()

def draw_health_bar(x, y, width, height, current_health, max_health, border_color, fill_color, back_color, label="", label_pos="above"):
    # Dibuja el texto de la etiqueta primero si está "arriba"
    if label and label_pos == "above":
        label_surf = info_font.render(label, True, WHITE)
        screen.blit(label_surf, (x, y - label_surf.get_height() - 5)) # 5 píxeles de padding

    back_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, back_color, back_rect)
    fill_width = int(width * (current_health / max_health))
    fill_rect = pygame.Rect(x, y, fill_width, height)
    pygame.draw.rect(screen, fill_color, fill_rect)
    pygame.draw.rect(screen, border_color, back_rect, 2)

    # Dibuja el texto de la etiqueta si está "debajo"
    if label and label_pos == "below":
        label_surf = info_font.render(label, True, WHITE)
        screen.blit(label_surf, (x, y + height + 5)) # 5 píxeles de padding

def draw_brasas(brazas):
    for b in brazas:
        b['y'] += b['speed']
        if b['y'] > HEIGHT:
            b['y'] = 0
            b['x'] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, ORANGE, (int(b['x']), int(b['y'])), 2)

# Segmento 3: Funciones de Pantallas de Información (Historia, Muerte, Victoria)

# Este segmento contiene la lógica para mostrar pantallas de información genéricas
# utilizadas para la historia del juego, mensajes de victoria o derrota.
# Incluye la función `mostrar_pantalla_info` y `mostrar_historia` que se usan
# para pausar el juego y presentar texto importante al jugador.

def mostrar_pantalla_info(titulo, descripcion, volver_a_menu=False):
    esperando = True

    titulo_font = pygame.font.SysFont("Arial Black", 36)
    descripcion_font = pygame.font.SysFont("Arial", 24)
    instruccion_font = pygame.font.SysFont("Arial", 20)

    while esperando:
        screen.fill(BLACK)
        draw_brasas(menu_brasas)

        panel_rect = pygame.Surface((600, 300), pygame.SRCALPHA)
        panel_rect.fill((0, 0, 0, 180))  # Negro con transparencia
        screen.blit(panel_rect, (WIDTH // 2 - 300, HEIGHT // 2 - 150))

        titulo_surf = titulo_font.render(titulo, True, ORANGE if "¡Has muerto!" not in titulo else RED)
        screen.blit(titulo_surf, (WIDTH // 2 - titulo_surf.get_width() // 2, HEIGHT // 2 - 130))

        lineas = descripcion.split("\n")
        for i, linea in enumerate(lineas):
            texto_surf = descripcion_font.render(linea, True, WHITE)
            screen.blit(texto_surf, (WIDTH // 2 - texto_surf.get_width() // 2, HEIGHT // 2 - 60 + i * 35))

        instruccion_text = "Presiona ENTER para continuar..."
        if volver_a_menu:
            instruccion_text = "Presiona ENTER para volver al menú..."
        instruccion = instruccion_font.render(instruccion_text, True, CYAN)
        screen.blit(instruccion, (WIDTH // 2 - instruccion.get_width() // 2, HEIGHT // 2 + 100))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                esperando = False

def mostrar_historia(nivel):
    historias = {
        1: ("UNA INFECCIÓN RARA Y PELIGROSA",
            "Un virus desconocido comenzó a propagarse entre la población.\nLos infectados ya no eran humanos..."),
        2: ("CIUDADES EN RUINAS",
            "La infección se ha extendido. Las ciudades han caído.\nPocos quedan en pie..."),
        3: ("ÚLTIMA RESISTENCIA",
            "Esta es tu última oportunidad.\nAcaba con el brote antes de que el mundo desaparezca.")
    }

    if nivel in historias:
        titulo, descripcion = historias[nivel]
        mostrar_pantalla_info(titulo, descripcion)

# Segmento 4: Inicialización de la Lógica del Juego (Variables de Estado)

# Este segmento define todas las variables iniciales para el estado del juego
# en `game_loop`. Esto incluye la posición del jugador, salud, XP, nivel,
# configuración de proyectiles, estado de los enemigos, y toda la información
# necesaria para controlar el flujo y las estadísticas del juego.

def game_loop():
    global run_game, show_menu

    # Partículas brasas fondo juego
    particles = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'radius': random.randint(1, 3),
                  'speed': random.uniform(0.2, 0.6)} for _ in range(120)]

    player_pos = [WIDTH // 2, HEIGHT // 2]
    # Adjust player_radius based on your character image size for better collision
    player_radius = 25 # Changed from 75, as the image is much smaller than 150x150, for more accurate collision

    base_speed = 4
    player_speed = base_speed
    player_health = 100
    player_max_health = 100
    player_xp = 0
    player_level = 1
    xp_to_next = 50

    nivel_actual = 1
    max_nivel = 3

    habilidad_actual = 1
    habilidad_nombres = {1: "Doble Tiro", 2: "Relentizador", 3: "Velocidad"}

    ralentizar_enemigos = False
    ralentizador_fin = 0

    projectiles = []
    projectile_speed = 7
    shoot_delay = 500
    last_shot_time = pygame.time.get_ticks()

    enemies = []
    enemy_spawn_delay = 1500
    last_enemy_spawn = pygame.time.get_ticks()
    enemy_base_speed = 1.5
    enemy_speed = enemy_base_speed

    jefe_activo = False
    jefe_pos = None
    jefe_vida = 0
    jefe_max_vida = 0
    jefe_danio = 10
    jefe_speed = 2
    jefe_proyectiles = []
    jefe_disparo_delay = 1000
    ultimo_disparo_jefe = 0

    # Lista para almacenar las manchas de sangre
    # Cada elemento será un diccionario {'x': x, 'y': y, 'alpha': 255}
    blood_stains = []

    mostrar_historia(nivel_actual)

    running = True

# Segmento 5: Bucle Principal del Juego (Eventos y Movimiento del Jugador)

# Este segmento contiene el corazón del bucle principal del juego (`while running`).
# Maneja la actualización de la pantalla (fondo y partículas), los eventos de entrada
# del usuario (teclado y ratón), el movimiento del jugador y la lógica de disparo
# automático de proyectiles. También incluye la gestión de las brasas de fondo
# y las manchas de sangre que se desvanecen.

    while running:
        dt = clock.tick(60)
        screen.fill((15, 15, 15))  # Fondo oscuro

        # Dibujar partículas (brasas)
        for p in particles:
            pygame.draw.circle(screen, ORANGE, (int(p['x']), int(p['y'])), p['radius'])
            p['y'] -= p['speed']
            if p['y'] < 0:
                p['x'] = random.randint(0, WIDTH)
                p['y'] = HEIGHT + random.randint(0, 100)
                p['speed'] = random.uniform(0.2, 0.6)

        # Dibujar manchas de sangre debajo de todo lo demás
        for stain in blood_stains[:]: # Iterar sobre una copia para poder eliminar elementos
            # Crea una superficie temporal para aplicar la transparencia
            stain_surface = blood_stain_img.copy()
            stain_surface.set_alpha(stain['alpha'])
            screen.blit(stain_surface, (stain['x'] - stain_surface.get_width() // 2, stain['y'] - stain_surface.get_height() // 2))
            stain['alpha'] -= 1 # Reducir la opacidad con el tiempo
            if stain['alpha'] <= 0:
                blood_stains.remove(stain)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_pos[1] -= player_speed
        if keys[pygame.K_s]: player_pos[1] += player_speed
        if keys[pygame.K_a]: player_pos[0] -= player_speed
        if keys[pygame.K_d]: player_pos[0] += player_speed

        # Keep player within screen bounds
        player_pos[0] = max(player_radius, min(player_pos[0], WIDTH - player_radius))
        player_pos[1] = max(player_radius, min(player_pos[1], HEIGHT - player_radius))


        now = pygame.time.get_ticks()

        # Disparar proyectiles automáticamente (cada shoot_delay ms)
        if now - last_shot_time >= shoot_delay:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - player_pos[0]
            dy = mouse_y - player_pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist
            projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx, 'dy': dy})
            weapon_shoot_sound.play() # Play weapon sound
            if habilidad_actual == 1:
                offset = math.pi / 12
                cos_off = math.cos(offset)
                sin_off = math.sin(offset)
                dx1, dy1 = dx * cos_off - dy * sin_off, dx * sin_off + dy * cos_off
                dx2, dy2 = dx * cos_off + dy * sin_off, -dx * sin_off + dy * cos_off
                projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx1, 'dy': dy1})
                projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx2, 'dy': dy2})
            last_shot_time = now

        for p in projectiles[:]:
            p['x'] += p['dx'] * projectile_speed
            p['y'] += p['dy'] * projectile_speed
            if not (0 <= p['x'] <= WIDTH and 0 <= p['y'] <= HEIGHT):
                projectiles.remove(p)
# Segmento 6: Lógica de Enemigos y Habilidades del Jugador

# Este segmento implementa la generación de enemigos, su movimiento para perseguir
# al jugador, y las colisiones entre enemigos y proyectiles.
# También gestiona la ganancia de XP, la subida de nivel del jugador y la activación
# de habilidades especiales como la ralentización de enemigos o el aumento de velocidad.

        if ralentizar_enemigos and now > ralentizador_fin:
            ralentizar_enemigos = False
            enemy_speed = enemy_base_speed

        if not jefe_activo and now - last_enemy_spawn >= enemy_spawn_delay:
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top': x, y = random.randint(0, WIDTH), 0
            elif side == 'bottom': x, y = random.randint(0, WIDTH), HEIGHT
            elif side == 'left': x, y = 0, random.randint(0, HEIGHT)
            else: x, y = WIDTH, random.randint(0, HEIGHT)
            enemy_img = random.choice(zombie_imgs)
            enemies.append({'x': x, 'y': y, 'speed': enemy_speed, 'img': enemy_img})
            zombie_spawn_sound.play() # Play zombie spawn sound
            last_enemy_spawn = now

        for enemy in enemies[:]:
            dx = player_pos[0] - enemy['x']
            dy = player_pos[1] - enemy['y']
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist
            enemy['x'] += dx * enemy['speed']
            enemy['y'] += dy * enemy['speed']

        # Fix for game crashing on enemy collision
        # Iterate over a copy of the list when modifying it
        for enemy in enemies[:]:
            if math.hypot(enemy['x'] - player_pos[0], enemy['y'] - player_pos[1]) < 40:
                player_health -= 1

            # Use a separate loop for projectiles to avoid skipping elements
            # due to concurrent modification if an enemy is removed.
            # This logic should be here to ensure XP and boss activation are checked for each enemy killed.
            for p in projectiles[:]:
                if math.hypot(enemy['x'] - p['x'], enemy['y'] - p['y']) < 30:
                    # Check if enemy still exists before trying to remove it
                    # This prevents the crash if the enemy was already removed
                    # by another projectile in the same frame.
                    if enemy in enemies: # Ensure the enemy is still in the list
                        # Añadir mancha de sangre en la posición del enemigo
                        blood_stains.append({'x': enemy['x'], 'y': enemy['y'], 'alpha': 255})

                        enemies.remove(enemy)
                        projectiles.remove(p)
                        player_xp += 10
                        if player_xp >= xp_to_next:
                            player_level += 1
                            player_xp = 0
                            xp_to_next += 25
                            # This block determines when the boss appears based on player level
                            if player_level == 2 and nivel_actual == 1:
                                jefe_activo = True
                                jefe_proyectiles.clear()
                                jefe_pos = [random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)]
                                jefe_vida = jefe_max_vida = 8
                                jefe_speed = 2
                                jefe_danio = 10
                                jefe_disparo_delay = 1200
                                enemies.clear() # Clear remaining regular enemies when boss appears
                            elif player_level == 3 and nivel_actual == 2:
                                jefe_activo = True
                                jefe_proyectiles.clear()
                                jefe_pos = [random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)]
                                jefe_vida = jefe_max_vida = 15
                                jefe_speed = 3
                                jefe_danio = 15
                                jefe_disparo_delay = 800
                                enemies.clear() # Clear remaining regular enemies when boss appears

                            # Modified for Fase 3: Boss appears when player reaches level 4
                            if player_level == 4 and nivel_actual == 3: # Boss for Nivel 3 appears when player reaches level 4
                                jefe_activo = True
                                jefe_proyectiles.clear()
                                jefe_pos = [random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)]
                                # Adjust boss 3 stats here to make it easier
                                jefe_vida = jefe_max_vida = 15 # Reduced from 25
                                jefe_speed = 3 # Reduced from 4.5
                                jefe_danio = 15 # Reduced from 25
                                jefe_disparo_delay = 600 # Increased from 400 (slower shots)
                                enemies.clear() # Clear remaining regular enemies when boss appears

                            # Habilidad update logic, independent of boss spawn
                            if player_level == 2 and habilidad_actual < 2:
                                habilidad_actual = 2
                            elif player_level >= 3 and habilidad_actual < 3: # Player level 3 or higher gets speed ability
                                habilidad_actual = 3


        if habilidad_actual == 2 and not ralentizar_enemigos and player_level >= 2: # Changed to >=2 as ability is gained at level 2
            if keys[pygame.K_SPACE]:
                ralentizar_enemigos = True
                enemy_speed = enemy_base_speed / 2.5
                ralentizador_fin = now + 5000

        if habilidad_actual == 3:
            player_speed = base_speed * 1.8
        elif habilidad_actual == 1 or habilidad_actual == 2: # Ensure speed resets if ability changes away from speed
             player_speed = base_speed

# Segmento 7: Lógica y Colisiones del Jefe Final
# Este segmento se encarga de todo lo relacionado con el jefe final:
# su movimiento para perseguir al jugador, la generación y movimiento de sus proyectiles,
# las colisiones con el jugador (tanto por contacto como por proyectiles),
# la reducción de su vida y la transición al siguiente nivel o victoria al ser derrotado.

        # Jefe
        if jefe_activo:
            dx = player_pos[0] - jefe_pos[0]
            dy = player_pos[1] - jefe_pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist
            jefe_pos[0] += dx * jefe_speed
            jefe_pos[1] += dy * jefe_speed

            if now - ultimo_disparo_jefe >= jefe_disparo_delay:
                jdx = player_pos[0] - jefe_pos[0]
                jdy = player_pos[1] - jefe_pos[1]
                dist = math.hypot(jdx, jdy)
                if dist != 0:
                    jdx /= dist
                    jdy /= dist
                jefe_proyectiles.append({'x': jefe_pos[0], 'y': jefe_pos[1], 'dx': jdx, 'dy': jdy})
                ultimo_disparo_jefe = now

            for j in jefe_proyectiles[:]:
                j['x'] += j['dx'] * 5
                j['y'] += j['dy'] * 5
                if not (0 <= j['x'] <= WIDTH and 0 <= j['y'] <= HEIGHT):
                    jefe_proyectiles.remove(j)
                elif math.hypot(j['x'] - player_pos[0], j['y'] - player_pos[1]) < player_radius:
                    player_health -= jefe_danio
                    jefe_proyectiles.remove(j)

            if math.hypot(jefe_pos[0] - player_pos[0], jefe_pos[1] - player_pos[1]) < player_radius + 25:
                player_health -= jefe_danio // 2

            for p in projectiles[:]:
                if math.hypot(jefe_pos[0] - p['x'], jefe_pos[1] - p['y']) < 30:
                    jefe_vida -= 1
                    projectiles.remove(p)

            if jefe_vida <= 0:
                # Añadir mancha de sangre en la posición del jefe al morir
                blood_stains.append({'x': jefe_pos[0], 'y': jefe_pos[1], 'alpha': 255})

                jefe_activo = False
                jefe_proyectiles.clear()
                nivel_actual += 1
                if nivel_actual <= max_nivel:
                    mostrar_historia(nivel_actual)
                enemy_speed += 0.7
                enemy_spawn_delay = max(400, enemy_spawn_delay - 250)
                # Ensure ability is set correctly after defeating a boss and advancing phase
                # This ensures the ability is correctly applied when entering a new phase.
                if nivel_actual == 2:
                    habilidad_actual = 2
                    player_speed = base_speed
                elif nivel_actual == 3:
                    habilidad_actual = 3
                    player_speed = base_speed * 1.8 # Re-apply speed boost for phase 3
                else: # For any level beyond 3, if you expand the game later
                    habilidad_actual = 3
                    player_speed = base_speed * 1.8

                ralentizar_enemigos = False # Reset slowdown after boss

# Segmento 8: Dibujo de Elementos del Juego y HUD
# Este segmento se encarga de dibujar todos los elementos visuales en la pantalla:
# el jugador, los enemigos, los proyectiles del jugador y del jefe, y el jefe mismo.
# También actualiza y dibuja el HUD (Heads-Up Display) con información vital
# como el nivel del jugador, XP, fase actual y la habilidad activa,
# incluyendo las barras de salud del jugador y del jefe.

        # Dibujar jugador
        screen.blit(personaje_img, (player_pos[0] - personaje_img.get_width() // 2, player_pos[1] - personaje_img.get_height() // 2))

        # Dibujar enemigos
        for enemy in enemies:
            screen.blit(enemy['img'], (enemy['x'] - enemy['img'].get_width() // 2, enemy['y'] - enemy['img'].get_height() // 2))

        # Dibujar proyectiles
        for p in projectiles:
            screen.blit(proyectil_img, (p['x'] - proyectil_img.get_width() // 2, p['y'] - proyectil_img.get_height() // 2))

        # Dibujar jefe
        if jefe_activo:
            jefe_img = jefe_imgs.get(nivel_actual)
            if jefe_img:
                screen.blit(jefe_img, (int(jefe_pos[0] - jefe_img.get_width() // 2), int(jefe_pos[1] - jefe_img.get_height() // 2)))
            else:
                pygame.draw.circle(screen, RED, (int(jefe_pos[0]), int(jefe_pos[1])), 30)
            for j in jefe_proyectiles:
                screen.blit(proyectil_jefe_img, (int(j['x'] - proyectil_jefe_img.get_width() // 2), int(j['y'] - proyectil_jefe_img.get_height() // 2)))

        # HUD
        screen.blit(info_font.render(f"Nivel: {player_level}", True, WHITE), (10, 10))
        screen.blit(info_font.render(f"XP: {player_xp}/{xp_to_next}", True, WHITE), (10, 35))
        screen.blit(info_font.render(f"Fase: {nivel_actual}", True, WHITE), (10, 60))
        screen.blit(info_font.render(f"Habilidad: {habilidad_nombres[habilidad_actual]}", True, WHITE), (10, 85))

        if habilidad_actual == 2 and ralentizar_enemigos:
            tiempo_restante = (ralentizador_fin - now) / 1000
            screen.blit(info_font.render(f"Ralentizador activo: {tiempo_restante:.1f}s", True, WHITE), (10, 110))

        # Barra de vida del jugador con etiqueta encima
        draw_health_bar(10, HEIGHT - 35, 200, 25, player_health, player_max_health, WHITE, GREEN, DARK_RED, "Barra de salud de Rick", "above")

        if jefe_activo:
            # Etiqueta para el jefe según la fase
            jefe_labels = {
                1: "Barra de salud del Portador",
                2: "Barra de salud del Acechador",
                3: "Barra de salud del Susurrador"
            }
            jefe_label_text = jefe_labels.get(nivel_actual, f"Jefe Fase {nivel_actual}") # Fallback por si no existe la etiqueta

            # Barra de vida del jefe con etiqueta debajo, reubicada para no sobreponerse
            # Calculamos la posición x para que esté centrado con la barra de vida
            jefe_bar_x = WIDTH - 260
            jefe_bar_y = 50 # Un poco más abajo que antes para dejar espacio para el texto

            draw_health_bar(jefe_bar_x, jefe_bar_y, 250, 25, jefe_vida, jefe_max_vida, WHITE, RED, DARK_RED, jefe_label_text, "below")

        if player_health <= 0:
            mostrar_pantalla_info("¡Has muerto!", "La infección ha consumido el mundo.\nNo hay esperanza...", volver_a_menu=True)
            running = False
            break

        if nivel_actual > max_nivel:
            mostrar_pantalla_info("¡HAS GANADO!", "El brote ha sido contenido.\nLa humanidad tiene una segunda oportunidad.", volver_a_menu=True)
            running = False
            break

        pygame.display.flip()

    run_game = False
    show_menu = True

def start_game():
    global run_game, show_menu
    run_game = True
    show_menu = False

def exit_game():
    pygame.quit()
    sys.exit()

def show_instructions_screen():
    global show_menu, show_instructions
    show_instructions = True
    show_menu = False

# Bucle principal
while True:
    clock.tick(60)

    if show_menu:
        screen.fill(BLACK)
        draw_brasas(menu_brasas)

        # Logotipo centrado arriba
        screen.blit(logotipo_img, (WIDTH // 2 - logotipo_img.get_width() // 2, 40))

        # Botones menú
        draw_button("Iniciar", WIDTH // 2 - 100, 360, 200, 50, ORANGE, LIGHT_ORANGE, start_game)
        draw_button("Instrucciones", WIDTH // 2 - 100, 430, 200, 50, ORANGE, LIGHT_ORANGE, show_instructions_screen)
        draw_button("Salir", WIDTH // 2 - 100, 500, 200, 50, ORANGE, LIGHT_ORANGE, exit_game)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.flip()

    elif show_instructions:
        mostrar_pantalla_info(
            "INSTRUCCIONES",
            "Muévete con W A S D\n"
            "Apunta con el ratón y dispara automáticamente\n"
            "Presiona ESPACIO para usar la habilidad del nivel 2\n"
            "¡Sobrevive y derrota a los jefes!",
            volver_a_menu=True
        )
        show_instructions = False
        show_menu = True

    elif run_game:
        game_loop()