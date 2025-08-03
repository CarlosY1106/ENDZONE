import pygame
import random
import math
import sys

# ---- Inicialización ----
pygame.init()
pygame.mixer.init()

# ---- Música ----
pygame.mixer.music.load("Sonido.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

# ---- Sonidos ----
zombie_spawn_sound = pygame.mixer.Sound("SonidoZombie.mp3")
zombie_spawn_sound.set_volume(0.2)
weapon_shoot_sound = pygame.mixer.Sound("SonidoArma.mp3")
weapon_shoot_sound.set_volume(0.1)

# ---- Pantalla ----
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EndZone")
clock = pygame.time.Clock()

# ---- Colores ----
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 140, 0)
LIGHT_ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GREEN = (0, 200, 0)
DARK_RED = (150, 0, 0)
DARK_GREEN = (0, 150, 0)

# ---- Fuentes ----
button_font = pygame.font.SysFont("Arial", 25)
info_font = pygame.font.SysFont("Arial", 20)

# ---- Función carga imagen ----
def cargar_imagen_ruta(ruta, ancho_objetivo, alto_objetivo):
    imagen = pygame.image.load(ruta).convert_alpha()
    original_ancho, original_alto = imagen.get_size()
    ratio = min(ancho_objetivo / original_ancho, alto_objetivo / original_alto)
    nuevo_tamano = (int(original_ancho * ratio), int(original_alto * ratio))
    return pygame.transform.smoothscale(imagen, nuevo_tamano)

# ---- Animación personaje desde spritesheet ----
sprite_sheet = pygame.image.load("Personaje_Movimiento.png").convert_alpha()
sheet_width, sheet_height = sprite_sheet.get_size()
frame_width = sheet_width // 4
frame_height = sheet_height // 3

def get_frames(sheet, frame_width, frame_height, start_row=0, cols=4, scale=0.6):
    frames = []
    for col in range(cols):
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (col * frame_width, start_row * frame_height, frame_width, frame_height))
        frame = pygame.transform.smoothscale(frame, (int(frame_width * scale), int(frame_height * scale)))
        frames.append(frame)
    return frames

personaje_frames = get_frames(sprite_sheet, frame_width, frame_height, start_row=0, cols=4, scale=0.6)
frame_index = 0
frame_timer = 0
animation_speed = 120

# ---- Imágenes ----
zombie_imgs = [cargar_imagen_ruta(f"Zombie{i}.png", 80, 80) for i in range(1, 16)]
proyectil_img = cargar_imagen_ruta("Proyectil.png", 20, 20)
proyectil_jefe_img = cargar_imagen_ruta("ProyectilZombie.png", 30, 30)
jefe_imgs = {
    1: cargar_imagen_ruta("JefeFinal1.png", 160, 160),
    2: cargar_imagen_ruta("JefeFinal2.png", 160, 160),
    3: cargar_imagen_ruta("JefeFinal3.png", 160, 160)
}
blood_stain_img = cargar_imagen_ruta("Sangre.png", 50, 50)
fondo_niveles = cargar_imagen_ruta("Fondo.png", WIDTH, HEIGHT)
logotipo_img = cargar_imagen_ruta("Logotipo.png", 300, 300)

# ---- Estados ----
show_menu = True
run_game = False
show_instructions = False

menu_brasas = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'speed': random.uniform(0.2, 0.6)} for _ in range(60)]
nubes = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'radius': random.randint(50, 90),
          'speed': random.uniform(0.05, 0.2), 'alpha': random.randint(20, 40)} for _ in range(6)]

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
    if label and label_pos == "above":
        label_surf = info_font.render(label, True, WHITE)
        screen.blit(label_surf, (x, y - label_surf.get_height() - 5))
    back_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, back_color, back_rect)
    fill_width = int(width * (current_health / max_health))
    pygame.draw.rect(screen, fill_color, (x, y, fill_width, height))
    pygame.draw.rect(screen, border_color, back_rect, 2)
    if label and label_pos == "below":
        label_surf = info_font.render(label, True, WHITE)
        screen.blit(label_surf, (x, y + height + 5))

def draw_brasas(brazas):
    for b in brazas:
        b['y'] += b['speed']
        if b['y'] > HEIGHT:
            b['y'] = 0; b['x'] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, ORANGE, (int(b['x']), int(b['y'])), 2)

def draw_nubes(nubes):
    for nube in nubes:
        nube['x'] -= nube['speed']
        if nube['x'] + nube['radius'] < 0:
            nube['x'] = WIDTH + nube['radius']
            nube['y'] = random.randint(0, HEIGHT // 2)
        cloud_surface = pygame.Surface((nube['radius']*2, nube['radius']), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud_surface, (200, 200, 200, nube['alpha']), (0, 0, nube['radius']*2, nube['radius']))
        screen.blit(cloud_surface, (nube['x'], nube['y']))

def mostrar_pantalla_info(titulo, descripcion, volver_a_menu=False):
    esperando = True
    titulo_font = pygame.font.SysFont("Arial Black", 36)
    descripcion_font = pygame.font.SysFont("Arial", 24)
    instruccion_font = pygame.font.SysFont("Arial", 20)
    while esperando:
        screen.fill(BLACK)
        draw_brasas(menu_brasas)
        panel_rect = pygame.Surface((600, 300), pygame.SRCALPHA)
        panel_rect.fill((0, 0, 0, 180))
        screen.blit(panel_rect, (WIDTH // 2 - 300, HEIGHT // 2 - 150))
        titulo_surf = titulo_font.render(titulo, True, ORANGE if "¡HAS MUERTO!" not in titulo else RED)
        screen.blit(titulo_surf, (WIDTH // 2 - titulo_surf.get_width() // 2, HEIGHT // 2 - 130))
        for i, linea in enumerate(descripcion.split("\n")):
            texto_surf = descripcion_font.render(linea, True, WHITE)
            screen.blit(texto_surf, (WIDTH // 2 - texto_surf.get_width() // 2, HEIGHT // 2 - 60 + i * 35))
        instruccion = instruccion_font.render("Presiona ENTER para continuar...", True, CYAN)
        screen.blit(instruccion, (WIDTH // 2 - instruccion.get_width() // 2, HEIGHT // 2 + 100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: esperando = False

def mostrar_historia(nivel):
    historias = {
        1: ("UNA INFECCIÓN RARA Y PELIGROSA", "Un virus desconocido comenzó a propagarse...\nLos infectados ya no eran humanos..."),
        2: ("CIUDADES EN RUINAS", "La infección se ha extendido. Las ciudades han caído.\nPocos quedan en pie..."),
        3: ("ÚLTIMA RESISTENCIA", "Esta es tu última oportunidad.\nAcaba con el brote antes de que el mundo desaparezca...")
    }
    if nivel in historias:
        titulo, descripcion = historias[nivel]
        mostrar_pantalla_info(titulo, descripcion)
# ============================
#          GAME LOOP
# ============================
def game_loop():
    global frame_index, frame_timer

    # ---- Variables de juego ----
    particles = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'radius': random.randint(1, 3), 'speed': random.uniform(0.2, 0.6)} for _ in range(120)]
    player_pos = [WIDTH // 2, HEIGHT // 2]
    player_radius = 25
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
    shoot_delay = 600
    last_shot_time = pygame.time.get_ticks()

    enemies = []
    enemy_spawn_delay = 1100
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

    blood_stains = []
    damage_flash = 0
    screen_shake = 0

    mostrar_historia(nivel_actual)
    running = True

    while running:
        dt = clock.tick(60)
        now = pygame.time.get_ticks()

        # ---- Vibración cámara ----
        offset_x = random.randint(-3, 3) if screen_shake > 0 else 0
        offset_y = random.randint(-3, 3) if screen_shake > 0 else 0
        if screen_shake > 0: screen_shake -= dt

        # ---- Fondo y partículas ----
        screen.blit(fondo_niveles, (0, 0))
        draw_nubes(nubes)
        for p in particles:
            pygame.draw.circle(screen, ORANGE, (int(p['x'])+offset_x, int(p['y'])+offset_y), p['radius'])
            p['y'] -= p['speed']
            if p['y'] < 0:
                p['x'] = random.randint(0, WIDTH)
                p['y'] = HEIGHT + random.randint(0, 100)
                p['speed'] = random.uniform(0.2, 0.6)

        # ---- Sangre ----
        for stain in blood_stains[:]:
            stain_surface = blood_stain_img.copy()
            stain_surface.set_alpha(stain['alpha'])
            screen.blit(stain_surface, (stain['x'] - stain_surface.get_width() // 2,
                                        stain['y'] - stain_surface.get_height() // 2))
            stain['alpha'] -= 1
            if stain['alpha'] <= 0: blood_stains.remove(stain)

        # ---- Eventos ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # ---- Movimiento jugador ----
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: player_pos[1] -= player_speed
        if keys[pygame.K_s]: player_pos[1] += player_speed
        if keys[pygame.K_a]: player_pos[0] -= player_speed
        if keys[pygame.K_d]: player_pos[0] += player_speed

        player_pos[0] = max(player_radius, min(player_pos[0], WIDTH - player_radius))
        player_pos[1] = max(player_radius, min(player_pos[1], HEIGHT - player_radius))

        # ---- Disparo ----
        if now - last_shot_time >= shoot_delay:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx, dy = mouse_x - player_pos[0], mouse_y - player_pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0: dx, dy = dx/dist, dy/dist
            projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx, 'dy': dy})
            weapon_shoot_sound.play()
            if habilidad_actual == 1:  # doble tiro
                offset = math.pi/12
                cos_off, sin_off = math.cos(offset), math.sin(offset)
                dx1, dy1 = dx*cos_off - dy*sin_off, dx*sin_off + dy*cos_off
                dx2, dy2 = dx*cos_off + dy*sin_off, -dx*sin_off + dy*cos_off
                projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx1, 'dy': dy1})
                projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx2, 'dy': dy2})
            last_shot_time = now

        for p in projectiles[:]:
            p['x'] += p['dx']*projectile_speed
            p['y'] += p['dy']*projectile_speed
            if not (0 <= p['x'] <= WIDTH and 0 <= p['y'] <= HEIGHT):
                projectiles.remove(p)

        # ---- Spawn enemigos ----
        if ralentizar_enemigos and now > ralentizador_fin:
            ralentizar_enemigos = False; enemy_speed = enemy_base_speed
        if not jefe_activo and now - last_enemy_spawn >= enemy_spawn_delay:
            side = random.choice(['top', 'bottom', 'left', 'right'])
            x, y = (random.randint(0, WIDTH), 0) if side=='top' else ((random.randint(0, WIDTH), HEIGHT) if side=='bottom' else ((0, random.randint(0, HEIGHT)) if side=='left' else (WIDTH, random.randint(0, HEIGHT))))
            enemy_img = random.choice(zombie_imgs)
            enemies.append({'x': x, 'y': y, 'speed': enemy_speed, 'img': enemy_img})
            zombie_spawn_sound.play()
            last_enemy_spawn = now

        for enemy in enemies:
            dx, dy = player_pos[0]-enemy['x'], player_pos[1]-enemy['y']
            dist = math.hypot(dx, dy)
            if dist != 0: dx, dy = dx/dist, dy/dist
            enemy['x'] += dx*enemy['speed']
            enemy['y'] += dy*enemy['speed']

        # ---- Colisiones ----
        enemies_to_remove = []
        projectiles_to_remove = []
        for enemy in enemies:
            if math.hypot(enemy['x']-player_pos[0], enemy['y']-player_pos[1]) < 40:
                player_health -= 1; damage_flash = 150; screen_shake = 300
            for p in projectiles:
                if math.hypot(enemy['x']-p['x'], enemy['y']-p['y']) < 30:
                    blood_stains.append({'x': enemy['x'], 'y': enemy['y'], 'alpha': 255})
                    enemies_to_remove.append(enemy)
                    projectiles_to_remove.append(p)
                    player_xp += 10
                    if player_xp >= xp_to_next:
                        player_level += 1; player_xp = 0; xp_to_next += 25
                        # ---- Activar jefe ----
                        if (player_level == 2 and nivel_actual == 1) or (player_level == 3 and nivel_actual == 2) or (player_level == 4 and nivel_actual == 3):
                            jefe_activo = True
                            jefe_pos = [random.randint(100, WIDTH-100), random.randint(100, HEIGHT-100)]
                            jefe_vida = jefe_max_vida = 8 + 7*(nivel_actual-1)
                            jefe_speed = 2 + (nivel_actual-1)
                            jefe_danio = 10 + 5*(nivel_actual-1)
                            jefe_disparo_delay = max(1200 - 200*(nivel_actual-1), 600)
                            jefe_proyectiles.clear()
                            enemies.clear()
                            screen_shake = 300
                        if player_level == 2 and habilidad_actual < 2: habilidad_actual = 2
                        elif player_level >= 3 and habilidad_actual < 3: habilidad_actual = 3
        for e in enemies_to_remove:
            if e in enemies: enemies.remove(e)
        for p in projectiles_to_remove:
            if p in projectiles: projectiles.remove(p)

        # ---- Jefe activo ----
        if jefe_activo:
            dx, dy = player_pos[0]-jefe_pos[0], player_pos[1]-jefe_pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0: dx, dy = dx/dist, dy/dist
            jefe_pos[0] += dx*jefe_speed
            jefe_pos[1] += dy*jefe_speed

            # Disparo del jefe
            if now - ultimo_disparo_jefe >= jefe_disparo_delay:
                jdx, jdy = player_pos[0]-jefe_pos[0], player_pos[1]-jefe_pos[1]
                dist = math.hypot(jdx, jdy)
                if dist != 0: jdx, jdy = jdx/dist, jdy/dist
                jefe_proyectiles.append({'x': jefe_pos[0], 'y': jefe_pos[1], 'dx': jdx, 'dy': jdy})
                ultimo_disparo_jefe = now

            for j in jefe_proyectiles[:]:
                j['x'] += j['dx']*5
                j['y'] += j['dy']*5
                if not (0 <= j['x'] <= WIDTH and 0 <= j['y'] <= HEIGHT):
                    jefe_proyectiles.remove(j)
                elif math.hypot(j['x']-player_pos[0], j['y']-player_pos[1]) < player_radius:
                    player_health -= jefe_danio; jefe_proyectiles.remove(j); damage_flash = 150; screen_shake = 300

            if math.hypot(jefe_pos[0]-player_pos[0], jefe_pos[1]-player_pos[1]) < player_radius+25:
                player_health -= jefe_danio//2; damage_flash = 150; screen_shake = 300

            for p in projectiles[:]:
                if math.hypot(jefe_pos[0]-p['x'], jefe_pos[1]-p['y']) < 30:
                    jefe_vida -= 1; projectiles.remove(p)

            if jefe_vida <= 0:
                blood_stains.append({'x': jefe_pos[0], 'y': jefe_pos[1], 'alpha': 255})
                jefe_activo = False; jefe_proyectiles.clear(); nivel_actual += 1
                if nivel_actual <= max_nivel: mostrar_historia(nivel_actual)
                enemy_speed += 0.7; enemy_spawn_delay = max(400, enemy_spawn_delay - 250)
                if nivel_actual == 2: habilidad_actual = 2; player_speed = base_speed
                elif nivel_actual == 3: habilidad_actual = 3; player_speed = base_speed*1.8
                ralentizar_enemigos = False

        if habilidad_actual == 2 and not ralentizar_enemigos and player_level >= 2:
            if keys[pygame.K_SPACE]:
                ralentizar_enemigos = True; enemy_speed = enemy_base_speed/2.5; ralentizador_fin = now + 5000
        if habilidad_actual == 3: player_speed = base_speed*1.8
        elif habilidad_actual in (1, 2): player_speed = base_speed

        # ---- Animación jugador ----
        is_moving = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
        if is_moving:
            if now - frame_timer > animation_speed:
                frame_index = (frame_index + 1) % len(personaje_frames)
                frame_timer = now
        else:
            frame_index = 0
        current_frame = personaje_frames[frame_index]
        screen.blit(current_frame, (player_pos[0]-current_frame.get_width()//2,
                                    player_pos[1]-current_frame.get_height()//2))

        # ---- Dibujo de enemigos, proyectiles, jefe ----
        for enemy in enemies:
            screen.blit(enemy['img'], (enemy['x']-enemy['img'].get_width()//2, enemy['y']-enemy['img'].get_height()//2))
        for p in projectiles:
            screen.blit(proyectil_img, (p['x']-proyectil_img.get_width()//2, p['y']-proyectil_img.get_height()//2))
        if jefe_activo:
            jefe_img = jefe_imgs.get(nivel_actual)
            if jefe_img: screen.blit(jefe_img, (int(jefe_pos[0]-jefe_img.get_width()//2), int(jefe_pos[1]-jefe_img.get_height()//2)))
            for j in jefe_proyectiles:
                screen.blit(proyectil_jefe_img, (int(j['x']-proyectil_jefe_img.get_width()//2), int(j['y']-proyectil_jefe_img.get_height()//2)))
            jefe_labels = {1:"Barra de salud del Portador", 2:"Barra de salud del Acechador", 3:"Barra de salud del Susurrador"}
            draw_health_bar(WIDTH-260, 50, 250, 25, jefe_vida, jefe_max_vida, WHITE, RED, DARK_RED, jefe_labels.get(nivel_actual, f"Jefe Fase {nivel_actual}"), "below")

        # ---- HUD ----
        screen.blit(info_font.render(f"Nivel: {player_level}", True, WHITE), (10, 10))
        screen.blit(info_font.render(f"XP: {player_xp}/{xp_to_next}", True, WHITE), (10, 35))
        screen.blit(info_font.render(f"Fase: {nivel_actual}", True, WHITE), (10, 60))
        screen.blit(info_font.render(f"Habilidad: {habilidad_nombres[habilidad_actual]}", True, WHITE), (10, 85))
        if habilidad_actual == 2 and ralentizar_enemigos:
            tiempo_restante = (ralentizador_fin-now)/1000
            screen.blit(info_font.render(f"Ralentizador activo: {tiempo_restante:.1f}s", True, WHITE), (10, 110))
        draw_health_bar(10, HEIGHT-35, 200, 25, player_health, player_max_health, WHITE, GREEN, DARK_RED, "Barra de salud de Rick", "above")

        if damage_flash > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((255, 0, 0))
            screen.blit(overlay, (0, 0))
            damage_flash -= dt

        if player_health <= 0:
            mostrar_pantalla_info("¡HAS MUERTO!", "La infección ha consumido el mundo.\nNo hay ninguna esperanza de vida...", True)
            running = False
        if nivel_actual > max_nivel:
            mostrar_pantalla_info("¡HAS GANADO!", "El brote ha sido contenido.\nLa humanidad tiene una segunda oportunidad...", True)
            running = False

        pygame.display.flip()

# ---- Menú ----
def start_game():
    global run_game, show_menu
    run_game = True; show_menu = False
def exit_game():
    pygame.quit(); sys.exit()
def show_instructions_screen():
    global show_menu, show_instructions
    show_instructions = True; show_menu = False

while True:
    clock.tick(60)
    if show_menu:
        screen.fill(BLACK)
        draw_brasas(menu_brasas)
        screen.blit(logotipo_img, (WIDTH//2 - logotipo_img.get_width()//2, 40))
        draw_button("Iniciar", WIDTH//2-100, 360, 200, 50, ORANGE, LIGHT_ORANGE, start_game)
        draw_button("Instrucciones", WIDTH//2-100, 430, 200, 50, ORANGE, LIGHT_ORANGE, show_instructions_screen)
        draw_button("Salir", WIDTH//2-100, 500, 200, 50, ORANGE, LIGHT_ORANGE, exit_game)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        pygame.display.flip()
    elif show_instructions:
        mostrar_pantalla_info("INSTRUCCIONES", "Muévete con W A S D\nApunta con el ratón y dispara automáticamente\nPresiona ESPACIO para usar el relentizador\n¡Sobrevive y derrota a los jefes!", True)
        show_instructions = False; show_menu = True
    elif run_game:
        game_loop()
