import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen Setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Crypto Escape Room")

# Colors (Dark Mode)
DARK_BG = (30, 30, 30)
DARK_TEXT = (220, 220, 220)
DARK_ACCENT = (50, 50, 50)
DARK_HIGHLIGHT = (70, 70, 70)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Fonts
FONT = pygame.font.Font(None, 36)

class CryptoEscapeRoom:
    def __init__(self):
        self.current_room = "start"
        self.challenges = [
            {
                "description": "Decode: KHOOR ZRUOG",
                "solution": "HELLO WORLD",
                "hint": "Shift each letter back 3 positions",
                "solved": False
            },
            {
                "description": "Decode: SGVsbG8gQ3liZXJTZWN1cml0eQ==",
                "solution": "Hello CyberSecurity",
                "hint": "Use base64 decoding method",
                "solved": False
            },
            {
                "description": "Decode: 43797065722053616665",
                "solution": "Cyper Safe",
                "hint": "Convert hex to ASCII text",
                "solved": False
            }
        ]
        self.current_challenge_index = 0
        self.user_input = ""
        self.input_active = False
        self.show_hint = False

    def draw_start_screen(self):
        screen.fill(DARK_BG)
        title = FONT.render("Crypto Escape Room", True, DARK_TEXT)
        start_text = FONT.render("Press SPACE to Begin", True, DARK_TEXT)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

    def draw_challenge_screen(self):
        screen.fill(DARK_BG)
        
        # Challenge Counter
        counter_text = FONT.render(f"Challenge: {self.current_challenge_index + 1}/{len(self.challenges)}", True, DARK_TEXT)
        screen.blit(counter_text, (20, 20))
        
        # Display current challenge description
        desc_text = FONT.render(self.challenges[self.current_challenge_index]["description"], True, DARK_TEXT)
        screen.blit(desc_text, (50, 100))

        # Input box
        input_box = pygame.Rect(200, 300, 400, 50)
        pygame.draw.rect(screen, DARK_ACCENT, input_box, 2)
        
        # Render user input
        input_surface = FONT.render(self.user_input, True, DARK_TEXT)
        screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))

        # Check solution button
        check_text = FONT.render("Check Solution", True, DARK_TEXT)
        check_button = pygame.Rect(300, 400, 200, 50)
        pygame.draw.rect(screen, DARK_HIGHLIGHT, check_button)
        screen.blit(check_text, (check_button.x + 20, check_button.y + 10))

        # Hint button
        hint_text = FONT.render("Hint", True, DARK_TEXT)
        hint_button = pygame.Rect(50, 500, 100, 50)
        pygame.draw.rect(screen, DARK_ACCENT, hint_button)
        screen.blit(hint_text, (hint_button.x + 25, hint_button.y + 10))

        # Render hint if active
        if self.show_hint:
            hint_surface = FONT.render(self.challenges[self.current_challenge_index]["hint"], True, GREEN)
            screen.blit(hint_surface, (200, 500))

        return input_box, check_button, hint_button

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.current_room == "start":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.current_room = "challenge"

                if self.current_room == "challenge":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        input_box, check_button, hint_button = self.draw_challenge_screen()
                        
                        # Activate input
                        if input_box.collidepoint(event.pos):
                            self.input_active = True
                        
                        # Check solution
                        if check_button.collidepoint(event.pos):
                            self._check_solution()
                        
                        # Show hint
                        if hint_button.collidepoint(event.pos):
                            self.show_hint = not self.show_hint

                    if event.type == pygame.KEYDOWN:
                        if self.input_active:
                            if event.key == pygame.K_RETURN:
                                self._check_solution()
                            elif event.key == pygame.K_BACKSPACE:
                                self.user_input = self.user_input[:-1]
                            else:
                                self.user_input += event.unicode

            # Draw screens
            if self.current_room == "start":
                self.draw_start_screen()
            elif self.current_room == "challenge":
                self.draw_challenge_screen()
            elif self.current_room == "win":
                screen.fill(DARK_BG)
                win_text = FONT.render("Congratulations! You Escaped!", True, GREEN)
                screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, SCREEN_HEIGHT//2))

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
        sys.exit()

    def _check_solution(self):
        if self.user_input.upper() == self.challenges[self.current_challenge_index]["solution"]:
            self.challenges[self.current_challenge_index]["solved"] = True
            self.current_challenge_index += 1
            self.user_input = ""
            
            # Check if all challenges are completed
            if self.current_challenge_index >= len(self.challenges):
                self.current_room = "win"
        
        self.input_active = False
        self.show_hint = False

# Run the game
if __name__ == "__main__":
    game = CryptoEscapeRoom()
    game.run()