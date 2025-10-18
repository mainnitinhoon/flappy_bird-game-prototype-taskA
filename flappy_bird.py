import pygame
import random
import sys
import os

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Game constants
WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.4
FLAP_STRENGTH = -8
PIPE_SPEED = 4
PIPE_GAP = 160
PIPE_FREQUENCY = 1200  # milliseconds

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)
SKY_BLUE = (135, 206, 235)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Create game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Up/Space=Flap, P=Pause, R=Restart, Q=Quit")
clock = pygame.time.Clock()

# Font
font = pygame.font.SysFont('Arial', 26)
small_font = pygame.font.SysFont('Arial', 20)

# --- Load Sounds ---
try:
    flap_sound = pygame.mixer.Sound("flap.wav")
    score_sound = pygame.mixer.Sound("score.wav")
    hit_sound = pygame.mixer.Sound("hit.wav")
except:
    flap_sound = score_sound = hit_sound = None
    print("⚠ Sound files not found. Place flap.wav, score.wav, hit.wav in same folder.")

# --- High score handling ---
def load_high_score():
    if os.path.exists("highscore.txt"):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_high_score(score):
    with open("highscore.txt", "w") as f:
        f.write(str(score))

# Bird class
class Bird:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.velocity = 0
        self.width = 35
        self.height = 35
    
    def flap(self):
        self.velocity = FLAP_STRENGTH
        if flap_sound: flap_sound.play()
    
    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity
    
    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.width, self.height), 0, 10)
        pygame.draw.circle(screen, BLACK, (self.x + 25, self.y + 10), 4)
        pygame.draw.polygon(screen, RED, [(self.x + 35, self.y + 15), 
                                          (self.x + 45, self.y + 15), 
                                          (self.x + 35, self.y + 20)])
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Pipe class
class Pipe:
    def __init__(self):
        self.x = WIDTH
        self.height = random.randint(150, 400)
        self.top_pipe = pygame.Rect(self.x, 0, 60, self.height)
        self.bottom_pipe = pygame.Rect(self.x, self.height + PIPE_GAP, 60, HEIGHT - self.height - PIPE_GAP)
        self.passed = False
    
    def move(self):
        self.x -= PIPE_SPEED
        self.top_pipe.x = self.x
        self.bottom_pipe.x = self.x
    
    def draw(self):
        pygame.draw.rect(screen, GREEN, self.top_pipe)
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.height - 20, 70, 20))
        pygame.draw.rect(screen, GREEN, self.bottom_pipe)
        pygame.draw.rect(screen, GREEN, (self.x - 5, self.height + PIPE_GAP, 70, 20))
    
    def collide(self, bird_rect):
        return self.top_pipe.colliderect(bird_rect) or self.bottom_pipe.colliderect(bird_rect)

# Game variables
bird = Bird()
pipes = []
score = 0
high_score = load_high_score()
last_pipe = pygame.time.get_ticks()

# States
game_active = False
game_paused = False
game_over = False

# --- Helper Draw Functions ---
def draw_score():
    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (10, 10))
    high_score_text = font.render(f'High Score: {high_score}', True, YELLOW)
    screen.blit(high_score_text, (WIDTH - 180, 10))

def draw_controls():
    controls_y = HEIGHT - 120
    controls = [
        "CONTROLS:",
        "UP/Space - Flap Bird",
        "P - Pause/Resume", 
        "R - Restart Game",
        "Q - Quit Game"
    ]
    for i, text in enumerate(controls):
        color = YELLOW if i == 0 else WHITE
        control_text = small_font.render(text, True, color)
        screen.blit(control_text, (10, controls_y + i * 25))

def draw_game_over():
    game_over_text = font.render('GAME OVER!', True, RED)
    restart_text = small_font.render('Press R to Restart', True, WHITE)
    final_score_text = small_font.render(f'Your Score: {score}', True, WHITE)
    high_score_text = small_font.render(f'High Score: {high_score}', True, YELLOW)
    screen.blit(game_over_text, (WIDTH//2 - 80, HEIGHT//2 - 50))
    screen.blit(final_score_text, (WIDTH//2 - 70, HEIGHT//2 - 10))
    screen.blit(high_score_text, (WIDTH//2 - 70, HEIGHT//2 + 10))
    screen.blit(restart_text, (WIDTH//2 - 90, HEIGHT//2 + 40))

def draw_pause():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    pause_text = font.render('GAME PAUSED', True, YELLOW)
    resume_text = small_font.render('Press P to Resume', True, WHITE)
    screen.blit(pause_text, (WIDTH//2 - 85, HEIGHT//2 - 30))
    screen.blit(resume_text, (WIDTH//2 - 85, HEIGHT//2 + 10))

def draw_start_screen():
    title = font.render("FLAPPY BIRD", True, YELLOW)
    prompt = small_font.render("Press SPACE or UP to Start", True, WHITE)
    hint = small_font.render("Avoid pipes and score high!", True, WHITE)
    screen.blit(title, (WIDTH//2 - 85, HEIGHT//2 - 60))
    screen.blit(prompt, (WIDTH//2 - 120, HEIGHT//2 - 10))
    screen.blit(hint, (WIDTH//2 - 100, HEIGHT//2 + 20))
    draw_controls()

def reset_game():
    global bird, pipes, score, game_active, last_pipe, game_over
    bird = Bird()
    pipes = []
    score = 0
    game_active = True
    game_over = False
    last_pipe = pygame.time.get_ticks()

# --- Main Game Loop ---
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_high_score(high_score)
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_q, pygame.K_DOWN):
                save_high_score(high_score)
                running = False
            
            if not game_active and not game_over and event.key in (pygame.K_SPACE, pygame.K_UP):
                reset_game()
            
            elif event.key in (pygame.K_SPACE, pygame.K_UP) and game_active and not game_paused:
                bird.flap()
            
            elif event.key == pygame.K_p and game_active:
                game_paused = not game_paused
            
            elif event.key == pygame.K_r:
                reset_game()
                game_paused = False

    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, (139, 69, 19), (0, HEIGHT - 50, WIDTH, 50))
    pygame.draw.rect(screen, (34, 139, 34), (0, HEIGHT - 50, WIDTH, 10))

    if not game_active and not game_over:
        draw_start_screen()

    elif game_active and not game_paused:
        bird.move()
        bird.draw()

        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > PIPE_FREQUENCY:
            pipes.append(Pipe())
            last_pipe = time_now

        for pipe in pipes[:]:
            pipe.move()
            pipe.draw()

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                score += 1
                if score_sound: score_sound.play()
                if score > high_score:
                    high_score = score

            if pipe.collide(bird.get_rect()):
                game_active = False
                game_over = True
                if hit_sound: hit_sound.play()

            if pipe.x < -60:
                pipes.remove(pipe)

        if bird.y > HEIGHT - 50 - bird.height or bird.y < 0:
            game_active = False
            game_over = True
            if hit_sound: hit_sound.play()

        draw_score()
        draw_controls()

    elif game_paused:
        bird.draw()
        for pipe in pipes:
            pipe.draw()
        draw_score()
        draw_controls()
        draw_pause()

    elif game_over:
        bird.draw()
        for pipe in pipes:
            pipe.draw()
        draw_score()
        draw_controls()
        draw_game_over()
        save_high_score(high_score)

    pygame.display.update()

pygame.quit()
sys.exit()