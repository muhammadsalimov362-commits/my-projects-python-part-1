# ============================================
# SPACE RUNNER — 5 УРОВНЕЙ + МАГАЗИН (M)
# ============================================
import pygame
import random
import json
import os
import math

pygame.init()
pygame.mixer.init()

# Настройки окна
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀 SPACE RUNNER")
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 150, 255)
CYAN = (50, 255, 255)
YELLOW = (255, 255, 0)
PURPLE = (150, 50, 255)
ORANGE = (255, 150, 50)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)

# Файлы данных
RECORD_FILE = "space_runner_record.json"
SHOP_FILE = "space_runner_shop.json"
ACHIEVEMENTS_FILE = "space_runner_achievements.json"
SKINS_FILE = "space_runner_skins.json"

def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

record = load_data(RECORD_FILE, 0)
shop_data = load_data(SHOP_FILE, {"stars": 0, "shield_level": 1, "slow_level": 1, "weapon_level": 0, "magnet": False})
achievements = load_data(ACHIEVEMENTS_FILE, {"survivor": False, "collector": False, "boss_slayer": False, "rich": False, "level_5": False})
owned_skins = load_data(SKINS_FILE, ["red"])
current_skin = "red"
current_level = 1
MAX_LEVELS = 5

font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)
small_font = pygame.font.Font(None, 24)

SKINS = {
    "red": {"main": RED, "dark": (150, 0, 0), "price": 0},
    "blue": {"main": BLUE, "dark": (0, 50, 150), "price": 100},
    "green": {"main": GREEN, "dark": (0, 150, 0), "price": 100},
    "gold": {"main": GOLD, "dark": (200, 150, 0), "price": 500},
    "neon": {"main": CYAN, "dark": (0, 150, 150), "price": 300},
    "purple": {"main": PURPLE, "dark": (100, 0, 100), "price": 200},
}

class Player:
    def __init__(self):
        self.x = 150
        self.y = HEIGHT // 2
        self.width = 40
        self.height = 30
        self.vel_y = 0
        self.gravity = 0.5
        self.jump_power = -10
        self.shield = False
        self.shield_timer = 0
        self.shield_max = 180 + (shop_data["shield_level"] - 1) * 60
        self.slow_mo = False
        self.slow_timer = 0
        self.slow_max = 120 + (shop_data["slow_level"] - 1) * 60
        self.weapon_level = shop_data["weapon_level"]
        self.magnet = shop_data["magnet"]
        self.double_jump = hasattr(Player, 'double_jump') and Player.double_jump
        self.jumps_left = 2
        
    def jump(self):
        self.vel_y = -15
        self.y -= 10
        print(f"JUMP! y={self.y}, vel_y={self.vel_y}")
        
    def update(self):
        self.vel_y += self.gravity
        self.y += self.vel_y
        
        if self.y < 0:
            self.y = 0
            self.vel_y = 0
        if self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.vel_y = 0
            self.jumps_left = 2
        
        if self.shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield = False
        
        if self.slow_mo:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.slow_mo = False
    
    def activate_shield(self):
        self.shield = True
        self.shield_timer = self.shield_max
    
    def activate_slow_mo(self):
        self.slow_mo = True
        self.slow_timer = self.slow_max
    
    def draw(self, screen):
        skin = SKINS[current_skin]
        color = CYAN if self.shield else skin["main"]
        pygame.draw.polygon(screen, color, [(self.x, self.y + self.height // 2), (self.x + self.width, self.y), (self.x + self.width, self.y + self.height)])
        pygame.draw.polygon(screen, skin["dark"], [(self.x, self.y + self.height // 2), (self.x + self.width, self.y), (self.x + self.width, self.y + self.height)], 2)
        if random.random() < 0.5:
            pygame.draw.polygon(screen, ORANGE, [(self.x - 5, self.y + 5), (self.x - 15, self.y + self.height // 2), (self.x - 5, self.y + self.height - 5)])
        if self.shield:
            pygame.draw.circle(screen, CYAN, (self.x + self.width // 2, self.y + self.height // 2), self.width + 5, 2)

class Obstacle:
    def __init__(self, speed=5):
        self.width = random.randint(30, 70)
        self.height = random.randint(30, 70)
        self.x = WIDTH
        self.y = random.randint(0, HEIGHT - self.height)
        self.speed = speed
        
    def update(self, slow_mo):
        self.x -= self.speed * (0.5 if slow_mo else 1)
        
    def draw(self, screen):
        pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (150, 0, 0), (self.x, self.y, self.width, self.height), 3)
        
    def off_screen(self):
        return self.x + self.width < 0
    
    def collide(self, player):
        return (self.x < player.x + player.width and self.x + self.width > player.x and self.y < player.y + player.height and self.y + self.height > player.y)

class MovingObstacle(Obstacle):
    def __init__(self, speed=5):
        super().__init__(speed)
        self.move_speed = random.choice([-2, 2])
        self.move_range = random.randint(50, 150)
        self.start_y = self.y
        
    def update(self, slow_mo):
        super().update(slow_mo)
        self.y += self.move_speed * (0.5 if slow_mo else 1)
        if abs(self.y - self.start_y) > self.move_range:
            self.move_speed *= -1

class Star:
    def __init__(self, speed=5):
        self.x = WIDTH
        self.y = random.randint(20, HEIGHT - 20)
        self.size = random.randint(8, 15)
        self.speed = speed
        
    def update(self, slow_mo, magnet=False, player=None):
        self.x -= self.speed * (0.5 if slow_mo else 1)
        if magnet and player:
            dx = player.x + player.width // 2 - self.x
            dy = player.y + player.height // 2 - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist < 150:
                self.x += dx / dist * 5
                self.y += dy / dist * 5
        
    def draw(self, screen):
        bright = random.randint(200, 255)
        pygame.draw.circle(screen, (bright, bright, 0), (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size // 2)
        
    def off_screen(self):
        return self.x + self.size < 0 or self.y < -50 or self.y > HEIGHT + 50
    
    def collect(self, player):
        return ((self.x - (player.x + player.width // 2)) ** 2 + (self.y - (player.y + player.height // 2)) ** 2) ** 0.5 < self.size + 25

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 15
        self.radius = 5
        
    def update(self):
        self.x += self.speed
        
    def draw(self, screen):
        pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius // 2)
        
    def off_screen(self):
        return self.x > WIDTH
    
    def hit(self, obs):
        return (self.x + self.radius > obs.x and self.x - self.radius < obs.x + obs.width and self.y > obs.y and self.y < obs.y + obs.height)

class Boss:
    def __init__(self, level):
        self.x = WIDTH - 150
        self.y = HEIGHT // 2 - 75
        self.width = 120
        self.height = 150
        self.hp = 10 + level * 5
        self.max_hp = self.hp
        self.speed = 2
        self.move_dir = 1
        self.shoot_timer = 0
        self.bullets = []
        
    def update(self, slow_mo):
        self.y += self.move_dir * self.speed * (0.5 if slow_mo else 1)
        if self.y < 0 or self.y > HEIGHT - self.height:
            self.move_dir *= -1
        self.shoot_timer += 1
        if self.shoot_timer > 30:
            self.bullets.append(BossBullet(self.x, self.y + self.height // 2))
            self.shoot_timer = 0
        for bullet in self.bullets[:]:
            bullet.update(slow_mo)
            if bullet.off_screen():
                self.bullets.remove(bullet)
        
    def draw(self, screen):
        pygame.draw.rect(screen, PURPLE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (100, 0, 100), (self.x, self.y, self.width, self.height), 5)
        bar_width = 100
        bar_height = 10
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (self.x + 10, self.y - 20, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (self.x + 10, self.y - 20, bar_width * hp_ratio, bar_height))
        for bullet in self.bullets:
            bullet.draw(screen)
    
    def collide(self, player):
        return (self.x < player.x + player.width and self.x + self.width > player.x and self.y < player.y + player.height and self.y + self.height > player.y)

class BossBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 7
        self.radius = 8
        
    def update(self, slow_mo):
        self.x -= self.speed * (0.5 if slow_mo else 1)
        
    def draw(self, screen):
        pygame.draw.circle(screen, PURPLE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius // 2)
        
    def off_screen(self):
        return self.x + self.radius < 0
    
    def hit(self, player):
        return ((self.x - (player.x + player.width // 2)) ** 2 + (self.y - (player.y + player.height // 2)) ** 2) ** 0.5 < self.radius + 25

class Background:
    def __init__(self):
        self.stars = []
        for _ in range(150):
            self.stars.append({'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'size': random.randint(1, 3), 'speed': random.uniform(0.5, 3)})
    
    def update(self, slow_mo):
        for star in self.stars:
            star['x'] -= star['speed'] * (0.3 if slow_mo else 1)
            if star['x'] < 0:
                star['x'] = WIDTH
                star['y'] = random.randint(0, HEIGHT)
    
    def draw(self, screen):
        for star in self.stars:
            bright = random.randint(100, 255)
            pygame.draw.circle(screen, (bright, bright, bright), (int(star['x']), int(star['y'])), star['size'])

def draw_text(text, font, color, x, y, center=True):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y)) if center else surface.get_rect(topleft=(x, y))
    screen.blit(surface, rect)

def draw_hud(score, rec, level, shield, slow_mo, stars):
    draw_text(f"SCORE: {score}", font, WHITE, 70, 30, center=False)
    draw_text(f"BEST: {rec}", font, YELLOW, 70, 60, center=False)
    draw_text(f"LEVEL: {level}/5", font, CYAN, WIDTH // 2, 30)
    draw_text(f"⭐ {stars}", font, GOLD, WIDTH - 70, 30, center=False)
    draw_text("M - SHOP", small_font, GRAY, WIDTH - 70, HEIGHT - 30, center=False)
    if shield:
        draw_text("🛡️", font, CYAN, WIDTH - 70, 60, center=False)
    if slow_mo:
        draw_text("⚡", font, BLUE, WIDTH - 100, 60, center=False)

def check_achievements(score, stars_collected, boss_killed, level):
    global achievements
    changed = False
    if score >= 1000 and not achievements["survivor"]:
        achievements["survivor"] = True
        changed = True
    if stars_collected >= 50 and not achievements["collector"]:
        achievements["collector"] = True
        changed = True
    if boss_killed and not achievements["boss_slayer"]:
        achievements["boss_slayer"] = True
        changed = True
    if shop_data["stars"] >= 1000 and not achievements["rich"]:
        achievements["rich"] = True
        changed = True
    if level >= 5 and not achievements["level_5"]:
        achievements["level_5"] = True
        changed = True
    if changed:
        save_data(ACHIEVEMENTS_FILE, achievements)
    return changed

def shop_screen():
    global shop_data, current_skin
    screen.fill(BLACK)
    draw_text("SHOP", big_font, GOLD, WIDTH // 2, 50)
    draw_text(f"⭐ STARS: {shop_data['stars']}", font, YELLOW, WIDTH // 2, 90)
    
    items = [
        ("🛡️ Shield Upgrade", shop_data["shield_level"] * 100, "shield"),
        ("⚡ Slow Upgrade", shop_data["slow_level"] * 100, "slow"),
        ("🔫 Weapon Lv." + str(shop_data["weapon_level"]), (shop_data["weapon_level"] + 1) * 200, "weapon"),
        ("🧲 Magnet", 300 if not shop_data["magnet"] else 0, "magnet"),
        ("🦅 Double Jump", 500, "double_jump"),
    ]
    
    y = 140
    for text, price, key in items:
        if key == "magnet" and shop_data["magnet"]:
            draw_text(f"{text} - OWNED", font, GREEN, WIDTH // 2, y)
        elif key == "double_jump" and hasattr(Player, 'double_jump') and Player.double_jump:
            draw_text(f"{text} - OWNED", font, GREEN, WIDTH // 2, y)
        else:
            color = GREEN if shop_data["stars"] >= price else RED
            draw_text(f"{text} - {price} ⭐", font, color, WIDTH // 2, y)
        y += 40
    
    draw_text("Press 1-5 to buy | ESC to exit", small_font, GRAY, WIDTH // 2, HEIGHT - 50)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
                prices = [shop_data["shield_level"]*100, shop_data["slow_level"]*100, (shop_data["weapon_level"]+1)*200, 300, 500]
                keys = ["shield_level", "slow_level", "weapon_level", "magnet", "double_jump"]
                for i, key_val in enumerate([pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]):
                    if event.key == key_val:
                        idx = i
                        if idx < len(prices):
                            key = keys[idx]
                            price = prices[idx]
                            if key == "magnet" and shop_data["magnet"]:
                                break
                            if key == "double_jump" and hasattr(Player, 'double_jump') and Player.double_jump:
                                break
                            if shop_data["stars"] >= price:
                                shop_data["stars"] -= price
                                if key in ["shield_level", "slow_level", "weapon_level"]:
                                    shop_data[key] += 1
                                elif key == "magnet":
                                    shop_data["magnet"] = True
                                elif key == "double_jump":
                                    Player.double_jump = True
                                save_data(SHOP_FILE, shop_data)
                                return True
    return True

def victory_screen(final_score):
    screen.fill(BLACK)
    draw_text("VICTORY!", big_font, GREEN, WIDTH // 2, HEIGHT // 2 - 80)
    draw_text("You completed all 5 levels!", font, WHITE, WIDTH // 2, HEIGHT // 2 - 20)
    draw_text(f"FINAL SCORE: {final_score}", font, YELLOW, WIDTH // 2, HEIGHT // 2 + 20)
    draw_text("Press SPACE to play again", small_font, GRAY, WIDTH // 2, HEIGHT // 2 + 100)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
    return True

def game_over_screen(score, rec, level, boss_killed):
    screen.fill(BLACK)
    draw_text("GAME OVER", big_font, RED, WIDTH // 2, HEIGHT // 2 - 80)
    draw_text(f"SCORE: {score}", font, WHITE, WIDTH // 2, HEIGHT // 2 - 20)
    draw_text(f"BEST: {rec}", font, YELLOW, WIDTH // 2, HEIGHT // 2 + 20)
    draw_text(f"LEVEL: {level}/5", font, CYAN, WIDTH // 2, HEIGHT // 2 + 60)
    if boss_killed:
        draw_text("BOSS DEFEATED!", font, GREEN, WIDTH // 2, HEIGHT // 2 + 100)
    draw_text("Press SPACE to restart", small_font, GRAY, WIDTH // 2, HEIGHT // 2 + 150)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
    return False

def level_complete_screen(level_num, score, stars):
    screen.fill(BLACK)
    if level_num == 5:
        return victory_screen(score)
    draw_text(f"LEVEL {level_num} COMPLETE!", big_font, GREEN, WIDTH // 2, HEIGHT // 2 - 50)
    draw_text(f"SCORE: {score}", font, WHITE, WIDTH // 2, HEIGHT // 2)
    draw_text(f"⭐ STARS: {stars}", font, GOLD, WIDTH // 2, HEIGHT // 2 + 40)
    draw_text("Press SPACE to continue", small_font, GRAY, WIDTH // 2, HEIGHT // 2 + 100)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return True
    return False

def game():
    global record, shop_data, achievements, current_level
    
    player = Player()
    player.double_jump = hasattr(Player, 'double_jump') and Player.double_jump
    obstacles = []
    stars_list = []
    bullets = []
    background = Background()
    boss = None
    
    score = 0
    level = current_level
    level_score = 0
    LEVEL_SCORE_TARGET = 500
    stars_collected = 0
    boss_killed = False
    frame_count = 0
    
    base_speed = 5
    base_spawn_delay = 60
    current_speed = base_speed + (level - 1) * 2
    spawn_delay = max(20, base_spawn_delay - (level - 1) * 10)
    
    if level % 3 == 0:
        boss = Boss(level)
        LEVEL_SCORE_TARGET = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed: {event.key}")
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    player.jump()
                    print("JUMP!")
                if event.key == pygame.K_s:
                    player.activate_shield()
                    print("SHIELD!")
                if event.key == pygame.K_d:
                    player.activate_slow_mo()
                    print("SLOW!")
                if event.key == pygame.K_f and shop_data["weapon_level"] > 0:
                    bullets.append(Bullet(player.x + player.width, player.y + player.height // 2))
                    print("SHOOT!")
                if event.key == pygame.K_m:
                    # Открываем магазин
                    shop_screen()
                    # Обновляем параметры игрока после покупок
                    player.shield_max = 180 + (shop_data["shield_level"] - 1) * 60
                    player.slow_max = 120 + (shop_data["slow_level"] - 1) * 60
                    player.weapon_level = shop_data["weapon_level"]
                    player.magnet = shop_data["magnet"]
                    player.double_jump = hasattr(Player, 'double_jump') and Player.double_jump
                    print("SHOP CLOSED")
        
        slow = player.slow_mo
        player.update()
        background.update(slow)
        
        if boss is None:
            frame_count += 1
            if frame_count >= spawn_delay:
                if random.random() < 0.6:
                    obs = Obstacle(current_speed) if random.random() < 0.7 else MovingObstacle(current_speed)
                    obstacles.append(obs)
                else:
                    stars_list.append(Star(current_speed))
                frame_count = 0
        
        if boss:
            boss.update(slow)
            if boss.collide(player) and not player.shield:
                if score > record:
                    record = score
                    save_data(RECORD_FILE, record)
                shop_data["stars"] += stars_collected
                save_data(SHOP_FILE, shop_data)
                return "game_over", score, level, boss_killed
            
            for bullet in boss.bullets[:]:
                if bullet.hit(player) and not player.shield:
                    if score > record:
                        record = score
                        save_data(RECORD_FILE, record)
                    shop_data["stars"] += stars_collected
                    save_data(SHOP_FILE, shop_data)
                    return "game_over", score, level, boss_killed
            
            for bullet in bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    bullets.remove(bullet)
                elif boss and bullet.x + bullet.radius > boss.x and bullet.x - bullet.radius < boss.x + boss.width and bullet.y > boss.y and bullet.y < boss.y + boss.height:
                    boss.hp -= 1
                    bullets.remove(bullet)
                    if boss.hp <= 0:
                        boss_killed = True
                        score += 500
                        stars_collected += 50
                        shop_data["stars"] += 50
                        boss = None
                        check_achievements(score, stars_collected, True, level)
                        return "level_complete", score, level, stars_collected
        else:
            for obs in obstacles[:]:
                obs.update(slow)
                if obs.off_screen():
                    obstacles.remove(obs)
                elif obs.collide(player):
                    if not player.shield:
                        if score > record:
                            record = score
                            save_data(RECORD_FILE, record)
                        shop_data["stars"] += stars_collected
                        save_data(SHOP_FILE, shop_data)
                        return "game_over", score, level, boss_killed
                    else:
                        obstacles.remove(obs)
            
            for bullet in bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    bullets.remove(bullet)
                else:
                    for obs in obstacles[:]:
                        if bullet.hit(obs):
                            obstacles.remove(obs)
                            bullets.remove(bullet)
                            score += 20
                            break
        
        for star in stars_list[:]:
            star.update(slow, player.magnet, player)
            if star.off_screen():
                stars_list.remove(star)
            elif star.collect(player):
                stars_list.remove(star)
                score += 10
                level_score += 10
                stars_collected += 1
                shop_data["stars"] += 1
        
        score += 1
        if boss is None:
            level_score += 1
        
        check_achievements(score, stars_collected, False, level)
        
        if boss is None and level_score >= LEVEL_SCORE_TARGET:
            shop_data["stars"] += stars_collected
            save_data(SHOP_FILE, shop_data)
            save_data(RECORD_FILE, record)
            return "level_complete", score, level, stars_collected
        
        # РУЧНОЕ УПРАВЛЕНИЕ
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            player.y -= 5
            print("MANUAL JUMP!")
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.y += 5
            print("MANUAL DOWN!")
        
        screen.fill(BLACK)
        background.draw(screen)
        player.draw(screen)
        for obs in obstacles:
            obs.draw(screen)
        for star in stars_list:
            star.draw(screen)
        for bullet in bullets:
            bullet.draw(screen)
        if boss:
            boss.draw(screen)
        
        draw_hud(score, record, level, player.shield, player.slow_mo, shop_data["stars"])
        if boss:
            draw_text("BOSS", big_font, PURPLE, WIDTH // 2, 100)
        else:
            draw_text(f"NEXT: {LEVEL_SCORE_TARGET - level_score}", small_font, GRAY, WIDTH // 2, 60)
        
        pygame.display.flip()
        clock.tick(60)
    
    return False

def main():
    global record, shop_data, current_level
    
    current_level = 1
    
    while current_level <= MAX_LEVELS:
        result = game()
        if not result:
            break
        if result[0] == "game_over":
            _, score, lvl, boss_killed = result
            if not game_over_screen(score, record, lvl, boss_killed):
                break
            current_level = 1
        elif result[0] == "level_complete":
            _, score, lvl, stars = result
            current_level = lvl + 1
            if current_level > MAX_LEVELS:
                victory_screen(score)
                current_level = 1
                break
            else:
                level_complete_screen(lvl, score, stars)
    
    save_data(RECORD_FILE, record)
    save_data(SHOP_FILE, shop_data)
    pygame.quit()

if __name__ == "__main__":
    main()