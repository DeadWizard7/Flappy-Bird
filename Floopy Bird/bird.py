import pygame, sys, random, os

# Initialize Game 
pygame.init()

# Window Setup
window_w, window_h = 400, 600
screen = pygame.display.set_mode((window_w, window_h))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
fps = 60

# Base directory
BASE_DIR = os.path.dirname(__file__)

# Helper to load assets safely
def load_asset(*path_parts):
    return os.path.join(BASE_DIR, *path_parts)

# Load Fonts
font_path = load_asset("fonts", "BaiJamjuree-Bold.ttf")
if os.path.exists(font_path):
    font_big = pygame.font.Font(font_path, 60)
    font_small = pygame.font.Font(font_path, 30)
else:
    font_big = pygame.font.SysFont("Arial", 60)
    font_small = pygame.font.SysFont("Arial", 30)

# Load Images
player_imgs = [
    pygame.image.load(load_asset("images", "redbird-midflap.png")),
    pygame.image.load(load_asset("images", "redbird-downflap.png")),
    pygame.image.load(load_asset("images", "redbird-upflap.png"))
]
pipe_up_img = pygame.image.load(load_asset("images", "pipe-red.png"))
pipe_down_img = pygame.image.load(load_asset("images", "pipe-red.png"))
ground_img = pygame.image.load(load_asset("images", "base.png"))
ground_width = ground_img.get_width()

bg_img = pygame.image.load(load_asset("images", "background-night.png"))
bg_img = pygame.transform.scale(bg_img, (window_w, window_h))
bg_width = bg_img.get_width()

over_img = pygame.image.load(load_asset("images", "gameover.png"))

# Load Sounds
try:
    slap_sfx = pygame.mixer.Sound(load_asset("sounds", "hit.wav"))
    woosh_sfx = pygame.mixer.Sound(load_asset("sounds", "wing.wav"))
    score_sfx = pygame.mixer.Sound(load_asset("sounds", "point.wav"))
except Exception:
    slap_sfx = woosh_sfx = score_sfx = None


# CLASSES 
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.frame = 0
        self.animation_timer = 0

    def jump(self):
        self.velocity = -10
        if woosh_sfx: woosh_sfx.play()

    def update(self):
        self.velocity += 0.75
        self.y += self.velocity
        self.animation_timer += 1
        if self.animation_timer >= 6:
            self.frame = (self.frame + 1) % len(player_imgs)
            self.animation_timer = 0

    def draw(self):
        screen.blit(player_imgs[self.frame], (self.x, self.y))

    def get_rect(self):
        img = player_imgs[self.frame]
        return pygame.Rect(self.x, self.y, img.get_width(), img.get_height())


class Pipe:
    def __init__(self, x, height, gap, velocity):
        self.x = x
        self.height = height
        self.gap = gap
        self.velocity = velocity
        self.scored = False

    def update(self):
        self.x -= self.velocity

    def draw(self):
        screen.blit(pipe_down_img, (self.x, self.height - pipe_down_img.get_height()))
        screen.blit(pipe_up_img, (self.x, self.height + self.gap))

    def get_rects(self):
        pipe_width = pipe_up_img.get_width()
        pipe_top_rect = pygame.Rect(self.x, 0, pipe_width, self.height)
        pipe_bottom_rect = pygame.Rect(self.x, self.height + self.gap, pipe_width, window_h - (self.height + self.gap))
        return pipe_top_rect, pipe_bottom_rect


#FUNCTIONS
def reset_game():
    global player, pipes, score, has_moved, game_state
    player = Player(168, 300)
    pipes = [Pipe(600, random.randint(30, 250), 220, 2.4)]
    score = 0
    has_moved = False
    game_state = "ready"


def draw_background(bg_x_pos, ground_x_pos):
    for i in range((window_w // bg_width) + 2):
        screen.blit(bg_img, (bg_x_pos + i * bg_width, 0))
    for i in range((window_w // ground_width) + 2):
        screen.blit(ground_img, (ground_x_pos + i * ground_width, 536))


def scoreboard(current_score):
    show_score = font_big.render(str(current_score), True, (10, 40, 9))
    score_rect = show_score.get_rect(center=(window_w // 2, 64))
    screen.blit(show_score, score_rect)


# GAME LOOP
def game():
    global game_state, score, has_moved, high_score

    bg_x_pos = 0
    ground_x_pos = 0
    high_score = 0

    reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_state == "ready":
                        has_moved = True
                        game_state = "play"
                        player.jump()
                    elif game_state == "play":
                        player.jump()
                    elif game_state == "over":
                        reset_game()

        if game_state == "ready":
            draw_background(bg_x_pos, ground_x_pos)
            title_text = font_big.render("Flappy Bird", True, (255, 255, 255))
            start_text = font_small.render("Press SPACE to Start", True, (255, 255, 0))
            high_text = font_small.render(f"Best: {high_score}", True, (255, 255, 255))

            screen.blit(title_text, (window_w//2 - title_text.get_width()//2, 100))
            screen.blit(start_text, (window_w//2 - start_text.get_width()//2, 200))
            screen.blit(high_text, (window_w//2 - high_text.get_width()//2, 260))
            player.draw()
            pygame.display.flip()

        elif game_state == "play":
            if has_moved:
                player.update()
                player_rect = player.get_rect()

                for pipe in pipes:
                    pipe.update()
                    top_rect, bottom_rect = pipe.get_rects()
                    if player_rect.colliderect(top_rect) or player_rect.colliderect(bottom_rect):
                        game_state = "over"
                        if slap_sfx: slap_sfx.play()

                if pipes[0].x < -pipe_up_img.get_width():
                    pipes.pop(0)
                    pipes.append(Pipe(400, random.randint(30, 280), 220, 2.4))

                for pipe in pipes:
                    if not pipe.scored and pipe.x + pipe_up_img.get_width() < player.x:
                        score += 1
                        if score_sfx: score_sfx.play()
                        pipe.scored = True
                        if score > high_score:
                            high_score = score

                if player.y < -64 or player.y > 536:
                    game_state = "over"
                    if slap_sfx: slap_sfx.play()

            bg_x_pos -= 1
            ground_x_pos -= 2
            if bg_x_pos <= -bg_width: bg_x_pos = 0
            if ground_x_pos <= -ground_width: ground_x_pos = 0

            draw_background(bg_x_pos, ground_x_pos)
            for pipe in pipes: pipe.draw()
            player.draw()
            scoreboard(score)
            pygame.display.flip()

        elif game_state == "over":
            draw_background(bg_x_pos, ground_x_pos)
            for pipe in pipes: pipe.draw()
            player.draw()
            scoreboard(score)
            screen.blit(over_img, (window_w//2 - over_img.get_width()//2, 200))
            high_text = font_small.render(f"Best: {high_score}", True, (255, 255, 255))
            screen.blit(high_text, (window_w//2 - high_text.get_width()//2, 300))
            restart_text = font_small.render("Press SPACE to Restart", True, (255, 255, 0))
            screen.blit(restart_text, (window_w//2 - restart_text.get_width()//2, 360))
            pygame.display.flip()

        clock.tick(fps)

game()
