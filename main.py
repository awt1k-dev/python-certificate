import pygame
from database import Database
import random
pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
YELLOW = (200,200,20)

font_large = pygame.font.SysFont('Arial', 48)
font_small = pygame.font.SysFont('Arial', 24)
font_medium = pygame.font.SysFont('Arial', 32)

clock = pygame.time.Clock()

# класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill(GREEN)

        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20

        self.speed = 7

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

# класс для создания врагов и коинов
class Cube(pygame.sprite.Sprite):
    def __init__(self, is_enemy=False):
        super().__init__()
        self.is_enemy = is_enemy

        self.image = pygame.Surface((30, 30))
        self.image.fill(RED if is_enemy else YELLOW)

        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - 30)
        self.rect.y = random.randint(-100, -40)

        self.speed = random.randint(3, 7)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - 30)
            self.rect.y = random.randint(-100, -40)
            self.speed = random.randint(3, 7)

def get_player_name(screen):
    name = ""
    input_active = True

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(name) > 0:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15 and event.unicode.isprintable():
                        name += event.unicode

        screen.fill(BLACK)

        label = font_medium.render("Введите ваше имя и нажмите Enter:", True, WHITE)
        name_text = font_large.render(name, True, WHITE)
        
        screen.blit(label, (WIDTH//2 - label.get_width()//2, HEIGHT//3))
        screen.blit(name_text, (WIDTH//2 - name_text.get_width()//2, HEIGHT//2))
        
        clock.tick(FPS)
        pygame.display.update()
    return name

def show_topers(screen, db, result_msg, final_score):
    top_5 = db.get_topers()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        screen.fill(BLACK)
        
        # Стата
        res_color = GREEN if "Победа" in result_msg else RED
        res_surf = font_large.render(result_msg, True, res_color)
        score_surf = font_medium.render(f"Ваш счет: {final_score}", True, WHITE)
        
        screen.blit(res_surf, (WIDTH//2 - res_surf.get_width()//2, 50))
        screen.blit(score_surf, (WIDTH//2 - score_surf.get_width()//2, 120))
        
        # Топеры
        top_title = font_medium.render("ТОП-5 ИГРОКОВ:", True, GRAY)
        screen.blit(top_title, (WIDTH//2 - top_title.get_width()//2, 200))
        
        margin = 250
        for i, (p_name, p_score) in enumerate(top_5):
            entry_text = font_small.render(f"{i+1}. {p_name} - {p_score} очков", True, WHITE)
            screen.blit(entry_text, (WIDTH//2 - entry_text.get_width()//2, margin))
            margin += 40
        
        # Выход
        exit_text = font_small.render("Нажмите ESC для выхода", True, GRAY)
        screen.blit(exit_text, (WIDTH//2 - exit_text.get_width()//2, HEIGHT - 50))

        clock.tick(FPS)
        pygame.display.update()

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Кубы")
    
    db = Database()
    
    player_name = get_player_name(screen)
    
    # Классы и группы
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    
    # Враги и коины
    for _ in range(5):
        coin = Cube(is_enemy=False)
        coins.add(coin)
        all_sprites.add(coin)
        
    for _ in range(3):
        enemy = Cube(is_enemy=True)
        enemies.add(enemy)
        all_sprites.add(enemy)
    
    score = 0
    running = True
    result_message = ""
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                db.close()
                pygame.quit()
                exit()

        all_sprites.update()
        
        # Coins
        hits = pygame.sprite.spritecollide(player, coins, True)
        for hit in hits:
            score += 1
            
            new_item = Cube(is_enemy=False)
            coins.add(new_item)
            all_sprites.add(new_item)
        
        # Enemies
        if pygame.sprite.spritecollideany(player, enemies):
            result_message = "Поражение! Вы задели красный куб."
            running = False

        # Win
        if score >= 10:
            result_message = "Победа! Вы собрали 10 кубов!"
            running = False

        screen.fill(BLACK)
        all_sprites.draw(screen)
        
        
        score_text = font_small.render(f"Очки: {score}/10", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        pygame.display.update()
        clock.tick(FPS)
        
    db.save_score(player_name, score)
    
    show_topers(screen, db, result_message, score)
    db.close()

main()