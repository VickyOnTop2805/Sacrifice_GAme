import pygame
import random
import math

# ---------- Config ----------
WIDTH, HEIGHT = 900, 600
FPS = 60
PLAYER_SPEED = 4.0
ENEMY_SPEED_BASE = 1.0
ENEMY_SPAWN_INTERVAL = 3.0
MAX_HEARTS = 5
ALLY_SPAWN_INTERVAL = 6.0
POWERUP_SPAWN_INTERVAL = 10.0
SHIELD_DURATION = 3.0  # seconds
FONT_NAME = None

def clamp(x, a, b): return max(a, min(b, x))
def distance(a,b): return math.hypot(a[0]-b[0], a[1]-b[1])

# ---------- Init ----------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sacrifices Must Be Made")
clock = pygame.time.Clock()
font = pygame.font.Font(FONT_NAME, 20)

# ---------- Classes ----------
class Player:
    def __init__(self, x, y, color, keys, name):
        self.x, self.y = x, y
        self.radius = 16
        self.hearts = 3
        self.color = color
        self.keys = keys
        self.shield_active = False
        self.shield_timer = 0
        self.alive = True
        self.name = name

    def pos(self): return (self.x, self.y)

    def update(self, dt, pressed):
        if not self.alive: return
        dx = dy = 0
        if pressed[self.keys["left"]]: dx -= 1
        if pressed[self.keys["right"]]: dx += 1
        if pressed[self.keys["up"]]: dy -= 1
        if pressed[self.keys["down"]]: dy += 1
        if dx or dy:
            mag = math.hypot(dx, dy)
            self.x += (dx/mag) * PLAYER_SPEED * dt * 60
            self.y += (dy/mag) * PLAYER_SPEED * dt * 60
        self.x = clamp(self.x, 20, WIDTH-20)
        self.y = clamp(self.y, 20, HEIGHT-20)

        # shield timer countdown
        if self.shield_active:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.shield_active = False

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
        if self.shield_active:
            s = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
            pygame.draw.circle(s, (255,255,255,180), (self.radius*2, self.radius*2), int(self.radius*2.5), 3)
            surf.blit(s, (int(self.x - self.radius*2), int(self.y - self.radius*2)))

class Enemy:
    def __init__(self):
        side = random.choice(['top','bottom','left','right'])
        if side == 'top': self.x, self.y = random.randint(0, WIDTH), -20
        elif side == 'bottom': self.x, self.y = random.randint(0, WIDTH), HEIGHT+20
        elif side == 'left': self.x, self.y = -20, random.randint(0, HEIGHT)
        else: self.x, self.y = WIDTH+20, random.randint(0, HEIGHT)
        self.radius = random.randint(12,18)
        self.speed = ENEMY_SPEED_BASE + random.random()*0.8
        self.alive = True

    def update(self, dt, players):
        targets = [p for p in players if p.alive]
        if not targets: return
        player = min(targets, key=lambda p: distance((self.x,self.y), p.pos()))
        dx, dy = player.x - self.x, player.y - self.y
        mag = math.hypot(dx, dy)
        if mag > 0.1:
            self.x += (dx/mag) * self.speed * dt * 60
            self.y += (dy/mag) * self.speed * dt * 60

    def draw(self, surf):
        pygame.draw.circle(surf, (178,34,34), (int(self.x), int(self.y)), self.radius)

class Ally:
    def __init__(self):
        self.x, self.y = random.randint(60, WIDTH-60), random.randint(60, HEIGHT-60)
        self.radius = 12
        self.sacrifice_required = random.random() < 0.35
        self.rescued = False

    def draw(self, surf):
        color = (240,230,140) if not self.rescued else (169,169,169)
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)

class HeartPowerUp:
    def __init__(self):
        self.x, self.y = random.randint(40, WIDTH-40), random.randint(40, HEIGHT-40)
        self.radius = 10
        self.active = True
    def draw(self, surf):
        if self.active:
            pygame.draw.circle(surf, (255,20,147), (self.x-5, self.y-5), 6)
            pygame.draw.circle(surf, (255,20,147), (self.x+5, self.y-5), 6)
            pygame.draw.polygon(surf, (255,20,147), [(self.x-11,self.y-2),(self.x+11,self.y-2),(self.x,self.y+12)])

# ---------- UI ----------
def draw_hearts(surf, x, y, hearts, color):
    for i in range(hearts):
        hx = x + i*20
        pygame.draw.circle(surf, color, (hx+6, y+6), 6)
        pygame.draw.circle(surf, color, (hx+14, y+6), 6)
        pygame.draw.polygon(surf, color, [(hx, y+8),(hx+20,y+8),(hx+10,y+20)])

def draw_text(surf, txt, x, y, size=20, color=(255,255,255)):
    f = pygame.font.Font(FONT_NAME, size)
    surf.blit(f.render(txt, True, color), (x,y))

def menu_screen():
    while True:
        screen.fill((18,18,30))
        draw_text(screen, "SACRIFICES MUST BE MADE", WIDTH//2-230, HEIGHT//2-120, 48)
        draw_text(screen, "Choose Mode", WIDTH//2-80, HEIGHT//2-40, 32, (200,200,200))
        draw_text(screen, "1 - Single Player", WIDTH//2-120, HEIGHT//2+20, 28)
        draw_text(screen, "2 - Two Players", WIDTH//2-120, HEIGHT//2+60, 28)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: return 1
                if e.key == pygame.K_2: return 2

def intro_screen():
    font_big = pygame.font.Font(FONT_NAME, 72)
    text = font_big.render("WE WORKED SO HARD FOR THIS", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))

    duration = 5000
    start_time = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()
        elapsed = now - start_time
        if elapsed >= duration: break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if elapsed < 1000: alpha = int(255 * (elapsed / 1000))
        elif elapsed > 4000: alpha = int(255 * ((duration - elapsed) / 1000))
        else: alpha = 255

        screen.fill((0, 0, 0))
        text_surf = text.copy()
        text_surf.set_alpha(alpha)
        screen.blit(text_surf, text_rect)

        pygame.display.flip()
        clock.tick(60)

# ---------- Game Loop ----------
def game_loop(mode):
    p1_keys = {"up":pygame.K_w,"down":pygame.K_s,"left":pygame.K_a,"right":pygame.K_d,"rescue":pygame.K_e,"shield":pygame.K_q}
    p2_keys = {"up":pygame.K_UP,"down":pygame.K_DOWN,"left":pygame.K_LEFT,"right":pygame.K_RIGHT,"rescue":pygame.K_RETURN,"shield":pygame.K_RSHIFT}

    if mode == 1:
        players = [Player(WIDTH//2, HEIGHT//2, (30,144,255), p1_keys, "P1")]
    else:
        p1 = Player(WIDTH//3, HEIGHT//2, (30,144,255), p1_keys, "P1")
        p2 = Player(2*WIDTH//3, HEIGHT//2, (50,205,50), p2_keys, "P2")
        players = [p1, p2]

    enemies, allies, powerups = [], [], []
    spawn_enemy, spawn_ally, spawn_power = 0,0,0
    score, rescued = 0,0
    game_over = False

    while True:
        dt = clock.tick(FPS)/1000.0
        keys = pygame.key.get_pressed()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: return
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
            for p in players:
                if not p.alive: continue
                if e.type == pygame.KEYDOWN:
                    if e.key == p.keys["shield"] and p.hearts>0:
                        p.hearts -= 1
                        p.shield_active = True
                        p.shield_timer = SHIELD_DURATION
                    if e.key == p.keys["rescue"]:
                        for ally in allies:
                            if not ally.rescued and distance(p.pos(), (ally.x,ally.y))<40:
                                if ally.sacrifice_required:
                                    if p.hearts>0: p.hearts -=1; ally.rescued=True; score+=200; rescued+=1
                                else: ally.rescued=True; score+=100; rescued+=1

        # update players
        for p in players: p.update(dt, keys)
        # spawn timers
        spawn_enemy += dt; spawn_ally += dt; spawn_power += dt
        if spawn_enemy > ENEMY_SPAWN_INTERVAL: enemies.append(Enemy()); spawn_enemy=0
        if spawn_ally > ALLY_SPAWN_INTERVAL: allies.append(Ally()); spawn_ally=0
        if spawn_power > POWERUP_SPAWN_INTERVAL: powerups.append(HeartPowerUp()); spawn_power=0

        # update enemies
        for e in enemies: e.update(dt, players)

        # collisions
        for e in enemies:
            for p in players:
                if p.alive and distance((e.x,e.y), p.pos()) < e.radius+p.radius:
                    if p.shield_active:
                        # shield blocks player hit
                        continue
                    else:
                        p.hearts -=1
                        if p.hearts<=0: p.alive=False

            # shield protects allies
            for ally in allies:
                if not ally.rescued and distance((e.x,e.y), (ally.x, ally.y)) < e.radius+ally.radius:
                    # check if any shield is near
                    protected = any(p.shield_active and distance(p.pos(), (ally.x, ally.y)) <= p.radius*2.5 for p in players)
                    if protected:
                        # push enemy away from shield
                        for p in players:
                            if p.shield_active and distance(p.pos(), (ally.x, ally.y)) <= p.radius*2.5:
                                dx = e.x - p.x
                                dy = e.y - p.y
                                mag = math.hypot(dx, dy)
                                if mag > 0:
                                    e.x += (dx/mag) * e.speed * dt * 60
                                    e.y += (dy/mag) * e.speed * dt * 60
                                break
                    else:
                        # could implement ally penalty if desired
                        pass

        # powerups
        for p in players:
            for pw in powerups:
                if pw.active and distance(p.pos(), (pw.x,pw.y)) < p.radius+pw.radius:
                    if p.hearts<MAX_HEARTS: p.hearts+=1
                    pw.active=False

        # check game over
        if not any(p.alive for p in players): game_over=True

        # draw
        screen.fill((25,25,40))
        for ally in allies: ally.draw(screen)
        for e in enemies: e.draw(screen)
        for pw in powerups: pw.draw(screen)
        for p in players: p.draw(screen)

        draw_text(screen,f"Score: {score}",20,20)
        draw_text(screen,f"Rescued: {rescued}",20,50)
        if len(players) >= 1:
            draw_hearts(screen, WIDTH-200, 20, players[0].hearts, (30,144,255))
            draw_text(screen,"P1", WIDTH-200, 50, 18,(200,200,255))
        if len(players) == 2:
            draw_hearts(screen, WIDTH-200, 80, players[1].hearts, (50,205,50))
            draw_text(screen,"P2", WIDTH-200, 110, 18,(200,255,200))

        if game_over:
            draw_text(screen,"GAME OVER", WIDTH//2-100, HEIGHT//2, 48, (255,180,180))

        # controls
        if len(players) == 1:
            draw_text(screen, "P1 Controls: Move=WASD | Rescue=E | Shield=Q", 20, HEIGHT-30, 18, (200,200,200))
        else:
            draw_text(screen, "P1: WASD Move | Rescue=E | Shield=Q     P2: Arrow Keys Move | Rescue=Enter | Shield=Right Shift", 20, HEIGHT-30, 18, (200,200,200))

        pygame.display.flip()

# ---------- Run ----------
mode = menu_screen()
intro_screen()
game_loop(mode)
pygame.quit()
