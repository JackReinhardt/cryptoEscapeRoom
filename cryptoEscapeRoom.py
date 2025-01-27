import pygame
import sys
import random
import base64
import codecs

# Initialize Pygame
pygame.init()

# Screen Setup
SCREEN_WIDTH = 1200  # Increased width for decoder panel
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
BLUE = (0, 150, 255)

# Fonts
FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 24)

class DecoderPanel:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.input_text = ""
        self.input_active = False
        self.output_text = ""
        self.current_cipher = "Caesar (+3)"
        self.ciphers = ["Caesar (+3)", "Caesar (-3)", "Base64", "Hex", "ROT13"]
        
    def decode(self, text):
        try:
            if self.current_cipher == "Caesar (+3)":
                return ''.join(chr((ord(c) - 65 + 3) % 26 + 65) if c.isupper() else 
                             chr((ord(c) - 97 + 3) % 26 + 97) if c.islower() else c
                             for c in text)
            elif self.current_cipher == "Caesar (-3)":
                return ''.join(chr((ord(c) - 65 - 3) % 26 + 65) if c.isupper() else 
                             chr((ord(c) - 97 - 3) % 26 + 97) if c.islower() else c
                             for c in text)
            elif self.current_cipher == "Base64":
                try:
                    return base64.b64decode(text).decode('utf-8')
                except:
                    return "Invalid Base64"
            elif self.current_cipher == "Hex":
                try:
                    return bytes.fromhex(text).decode('utf-8')
                except:
                    return "Invalid Hex"
            elif self.current_cipher == "ROT13":
                return codecs.encode(text, 'rot_13')
        except:
            return "Decoding Error"
        
    def draw(self, screen):
        # Draw panel background
        pygame.draw.rect(screen, DARK_ACCENT, (self.x, self.y, self.width, self.height))
        
        # Title
        title = FONT.render("Decoder Panel", True, DARK_TEXT)
        screen.blit(title, (self.x + 10, self.y + 10))
        
        # Input box
        input_box = pygame.Rect(self.x + 10, self.y + 60, self.width - 20, 40)
        pygame.draw.rect(screen, DARK_BG if self.input_active else DARK_HIGHLIGHT, input_box)
        input_surface = SMALL_FONT.render(self.input_text, True, DARK_TEXT)
        screen.blit(input_surface, (input_box.x + 5, input_box.y + 10))
        
        # Cipher selection buttons
        y_offset = 120
        button_height = 30
        for cipher in self.ciphers:
            button_rect = pygame.Rect(self.x + 10, self.y + y_offset, self.width - 20, button_height)
            pygame.draw.rect(screen, BLUE if cipher == self.current_cipher else DARK_HIGHLIGHT, button_rect)
            text = SMALL_FONT.render(cipher, True, DARK_TEXT)
            screen.blit(text, (button_rect.x + 5, button_rect.y + 5))
            y_offset += button_height + 5
        
        # Output
        output_label = SMALL_FONT.render("Output:", True, DARK_TEXT)
        screen.blit(output_label, (self.x + 10, self.y + y_offset + 10))
        output_surface = SMALL_FONT.render(self.output_text, True, GREEN)
        screen.blit(output_surface, (self.x + 10, self.y + y_offset + 40))
        
        return input_box, [pygame.Rect(self.x + 10, self.y + 120 + i*(button_height + 5), 
                          self.width - 20, button_height) for i in range(len(self.ciphers))]

class CryptoEscapeRoom:
    def __init__(self):
        self.current_room = "start"
        self.challenges = [
            {
                "description": "Decode: KHOOR ZRUOG",
                "solution": "HELLO WORLD",
                "hint": "Shift each letter back 3 positions (Caesar -3)",
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
        self.decoder = DecoderPanel(800, 0, 400, 600)

    def draw_start_screen(self):
        screen.fill(DARK_BG)
        title = FONT.render("Crypto Escape Room", True, DARK_TEXT)
        start_text = FONT.render("Press SPACE to Begin", True, DARK_TEXT)
        screen.blit(title, (400 - title.get_width()//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(start_text, (400 - start_text.get_width()//2, SCREEN_HEIGHT//2 + 50))

    def draw_challenge_screen(self):
        # Main game area
        pygame.draw.rect(screen, DARK_BG, (0, 0, 800, SCREEN_HEIGHT))
        
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

        # Draw decoder panel
        decoder_input_box, cipher_buttons = self.decoder.draw(screen)

        return input_box, check_button, hint_button, decoder_input_box, cipher_buttons

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
                        input_box, check_button, hint_button, decoder_input_box, cipher_buttons = self.draw_challenge_screen()
                        
                        # Main game input
                        if input_box.collidepoint(event.pos):
                            self.input_active = True
                            self.decoder.input_active = False
                        
                        # Decoder input
                        elif decoder_input_box.collidepoint(event.pos):
                            self.decoder.input_active = True
                            self.input_active = False
                        
                        # Check solution
                        elif check_button.collidepoint(event.pos):
                            self._check_solution()
                        
                        # Show hint
                        elif hint_button.collidepoint(event.pos):
                            self.show_hint = not self.show_hint
                            
                        # Cipher selection
                        for button, cipher in zip(cipher_buttons, self.decoder.ciphers):
                            if button.collidepoint(event.pos):
                                self.decoder.current_cipher = cipher
                                self.decoder.output_text = self.decoder.decode(self.decoder.input_text)

                    if event.type == pygame.KEYDOWN:
                        if self.input_active:
                            if event.key == pygame.K_RETURN:
                                self._check_solution()
                            elif event.key == pygame.K_BACKSPACE:
                                self.user_input = self.user_input[:-1]
                            else:
                                self.user_input += event.unicode
                        elif self.decoder.input_active:
                            if event.key == pygame.K_BACKSPACE:
                                self.decoder.input_text = self.decoder.input_text[:-1]
                            else:
                                self.decoder.input_text += event.unicode
                            self.decoder.output_text = self.decoder.decode(self.decoder.input_text)

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