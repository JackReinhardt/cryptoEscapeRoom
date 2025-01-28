import pygame
import sys
import random
import base64
import codecs
import binascii
import textwrap
from collections import OrderedDict

# Initialize Pygame
pygame.init()

# Screen Setup
SCREEN_WIDTH = 1200
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

def wrap_text(text, font, max_width):
    """Wrap text to fit within a given width."""
    text = str(text)
    words = text.split(" ")
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_surface = font.render(word + ' ', True, DARK_TEXT)
        word_width = word_surface.get_width()

        if current_width + word_width <= max_width:
            current_line.append(word)
            current_width += word_width
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width

    if current_line:
        lines.append(' '.join(current_line))

    return lines

class Cipher:
    @staticmethod
    def vigenere_decode(text, key):
        result = ""
        key_length = len(key)
        key_as_int = [ord(i) for i in key.upper()]
        text_int = [ord(i) for i in text.upper()]
        for i in range(len(text_int)):
            if chr(text_int[i]).isalpha():
                value = (text_int[i] - key_as_int[i % key_length]) % 26
                result += chr(value + 65)
            else:
                result += chr(text_int[i])
        return result
    
    @staticmethod
    def polybius_decode(text):
        square = {
            '11': 'A', '12': 'B', '13': 'C', '14': 'D', '15': 'E',
            '21': 'F', '22': 'G', '23': 'H', '24': 'I', '25': 'K',
            '31': 'L', '32': 'M', '33': 'N', '34': 'O', '35': 'P',
            '41': 'Q', '42': 'R', '43': 'S', '44': 'T', '45': 'U',
            '51': 'V', '52': 'W', '53': 'X', '54': 'Y', '55': 'Z'
        }
        result = ""
        # Remove any spaces from the input
        text = text.replace(" ", "")
        # Process pairs of numbers
        for i in range(0, len(text), 2):
            if i + 1 < len(text):
                pair = text[i:i+2]
                if pair in square:
                    result += square[pair]
        return result

    @staticmethod
    def rail_fence_decode(text, rails):
        if rails < 2:
            return text
        
        fence = [[''] * len(text) for _ in range(rails)]
        rail = 0
        direction = 1
        
        # Mark fence positions
        for i in range(len(text)):
            fence[rail][i] = '*'
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        
        # Fill fence with text
        index = 0
        for i in range(rails):
            for j in range(len(text)):
                if fence[i][j] == '*':
                    fence[i][j] = text[index]
                    index += 1
        
        # Read off fence
        result = ''
        rail = 0
        direction = 1
        for i in range(len(text)):
            result += fence[rail][i]
            rail += direction
            if rail == rails - 1 or rail == 0:
                direction = -direction
        
        return result

class DecoderPanel:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.input_text = ""
        self.input_active = False
        self.output_text = ""
        self.current_cipher = "Caesar (-3)"
        self.caesar_shift = 3
        self.rail_fence_rails = 3
        self.vigenere_key = "KEY"
        self.ciphers = [
            "Caesar (+N)", 
            "Caesar (-N)", 
            "ROT13",
            "Vigenere",
            "Rail Fence",
            "Polybius Square",
            "Atbash",
            "Reverse Text"
        ]
        
    def decode(self, text):
        try:
            if not text:
                return ""
                
            if self.current_cipher == "Caesar (+N)":
                return ''.join(chr((ord(c) - 65 + self.caesar_shift) % 26 + 65) if c.isupper() else 
                             chr((ord(c) - 97 + self.caesar_shift) % 26 + 97) if c.islower() else c
                             for c in text)
            elif self.current_cipher == "Caesar (-N)":
                return ''.join(chr((ord(c) - 65 - self.caesar_shift) % 26 + 65) if c.isupper() else 
                             chr((ord(c) - 97 - self.caesar_shift) % 26 + 97) if c.islower() else c
                             for c in text)
            elif self.current_cipher == "ROT13":
                return codecs.encode(text, 'rot_13')
            elif self.current_cipher == "Vigenere":
                return Cipher.vigenere_decode(text, self.vigenere_key)
            elif self.current_cipher == "Rail Fence":
                return Cipher.rail_fence_decode(text, self.rail_fence_rails)
            elif self.current_cipher == "Polybius Square":
                return Cipher.polybius_decode(text)
            elif self.current_cipher == "Atbash":
                return ''.join(chr(155 - ord(c)) if 'A' <= c <= 'Z' else
                             chr(219 - ord(c)) if 'a' <= c <= 'z' else c
                             for c in text)
            elif self.current_cipher == "Reverse Text":
                return text[::-1]
        except:
            return "Decoding Error"
        
    def draw(self, screen):
        # Draw panel background
        pygame.draw.rect(screen, DARK_ACCENT, (self.x, self.y, self.width, self.height))
        
        # Title
        title = FONT.render("Decoder Panel", True, DARK_TEXT)
        screen.blit(title, (self.x + 10, self.y + 10))
        
        # Input box with text wrapping
        input_box = pygame.Rect(self.x + 10, self.y + 60, self.width - 20, 60)
        pygame.draw.rect(screen, DARK_BG if self.input_active else DARK_HIGHLIGHT, input_box)
        
        # Wrap and render input text
        wrapped_input = wrap_text(self.input_text, SMALL_FONT, self.width - 40)
        for i, line in enumerate(wrapped_input):
            input_surface = SMALL_FONT.render(line, True, DARK_TEXT)
            screen.blit(input_surface, (input_box.x + 5, input_box.y + 5 + (i * 20)))

        # Create and draw cipher buttons
        cipher_buttons = []
        for i, cipher in enumerate(self.ciphers):
            button = pygame.Rect(self.x + 10, self.y + 130 + (i * 35), self.width - 20, 30)
            cipher_buttons.append(button)
            pygame.draw.rect(screen, DARK_HIGHLIGHT if cipher == self.current_cipher else DARK_BG, button)
            cipher_text = SMALL_FONT.render(cipher, True, DARK_TEXT)
            screen.blit(cipher_text, (button.x + 10, button.y + 5))

        # Output text area
        output_box = pygame.Rect(self.x + 10, self.y + 130 + (len(self.ciphers) * 35), self.width - 20, 60)
        pygame.draw.rect(screen, DARK_BG, output_box)
        
        # Wrap and render output text
        wrapped_output = wrap_text(self.output_text, SMALL_FONT, self.width - 40)
        for i, line in enumerate(wrapped_output):
            output_surface = SMALL_FONT.render(line, True, DARK_TEXT)
            screen.blit(output_surface, (output_box.x + 5, output_box.y + 5 + (i * 20)))

        # Initialize parameter buttons as None
        parameter_buttons = (None, None)
        
        if self.current_cipher in ["Caesar (+N)", "Caesar (-N)"]:
            shift_text = SMALL_FONT.render(f"Shift: {self.caesar_shift}", True, DARK_TEXT)
            screen.blit(shift_text, (self.x + 10, self.y + 450))
            
            # Add +/- buttons for shift
            minus_btn = pygame.Rect(self.x + 100, self.y + 450, 20, 20)
            plus_btn = pygame.Rect(self.x + 130, self.y + 450, 20, 20)
            pygame.draw.rect(screen, DARK_HIGHLIGHT, minus_btn)
            pygame.draw.rect(screen, DARK_HIGHLIGHT, plus_btn)
            
            screen.blit(SMALL_FONT.render("-", True, DARK_TEXT), (minus_btn.x + 7, minus_btn.y + 2))
            screen.blit(SMALL_FONT.render("+", True, DARK_TEXT), (plus_btn.x + 5, plus_btn.y + 2))
            
            parameter_buttons = (minus_btn, plus_btn)
            
        elif self.current_cipher == "Rail Fence":
            rails_text = SMALL_FONT.render(f"Rails: {self.rail_fence_rails}", True, DARK_TEXT)
            screen.blit(rails_text, (self.x + 10, self.y + 450))
            
            minus_btn = pygame.Rect(self.x + 100, self.y + 450, 20, 20)
            plus_btn = pygame.Rect(self.x + 130, self.y + 450, 20, 20)
            pygame.draw.rect(screen, DARK_HIGHLIGHT, minus_btn)
            pygame.draw.rect(screen, DARK_HIGHLIGHT, plus_btn)
            
            screen.blit(SMALL_FONT.render("-", True, DARK_TEXT), (minus_btn.x + 7, minus_btn.y + 2))
            screen.blit(SMALL_FONT.render("+", True, DARK_TEXT), (plus_btn.x + 5, plus_btn.y + 2))
            
            parameter_buttons = (minus_btn, plus_btn)
            
        elif self.current_cipher == "Vigenere":
            key_text = SMALL_FONT.render(f"Key: {self.vigenere_key}", True, DARK_TEXT)
            screen.blit(key_text, (self.x + 10, self.y + 450))
        
        return input_box, cipher_buttons, parameter_buttons
    
class CryptoEscapeRoom:
    def __init__(self):
        self.current_room = "start"
        self.challenges = [
            {
                "description": "Decode: KHOOR ZRUOG",
                "solution": "HELLO WORLD",
                "hint": "Use Caesar (-3) - shift each letter back 3 positions",
                "solved": False
            },
            {
                "description": "Decode: 24 33 44 15 33 43 24 44 54",
                "solution": "INTENSITY",
                "hint": "Use the Polybius Square cipher - each pair of numbers represents a letter",
                "solved": False
            },
            {
                "description": "Decode: SVOOL DLIOW",
                "solution": "HELLO TEAM",
                "hint": "Use the Atbash cipher - each letter is replaced with its opposite in the alphabet",
                "solved": False
            },
            {
                "description": "Decode: URYYB JBEYQ",
                "solution": "HELLO WORLD",
                "hint": "Use ROT13 - rotate each letter 13 positions",
                "solved": False
            },
            {
                "description": "Decode: DLROW OLLEH",
                "solution": "HELLO WORLD",
                "hint": "Use Reverse Text - read the message backwards",
                "solved": False
            },
            {
                "description": "Decode: RIJVS ASNVHR",
                "solution": "HELLO THERE",
                "hint": "Use Vigenere cipher with key 'KEY'",
                "solved": False
            },
            {
                "description": "Decode: HOOD ELWRL LOL",
                "solution": "HELLO WORLD",
                "hint": "Use Rail Fence with 3 rails",
                "solved": False
            },
            {
                "description": "Decode: MJQQT BTWQI",
                "solution": "HELLO WORLD",
                "hint": "Use Caesar (+5) - shift each letter forward 5 positions",
                "solved": False
            }
        ]
        self.current_challenge_index = 0
        self.user_input = ""
        self.input_active = False
        self.show_hint = False
        self.decoder = DecoderPanel(800, 0, 400, 600)

    def handle_parameter_buttons(self, pos, parameter_buttons):
        minus_btn, plus_btn = parameter_buttons
        if self.decoder.current_cipher in ["Caesar (+N)", "Caesar (-N)"]:
            if minus_btn.collidepoint(pos):
                self.decoder.caesar_shift = max(1, self.decoder.caesar_shift - 1)
            elif plus_btn.collidepoint(pos):
                self.decoder.caesar_shift = min(25, self.decoder.caesar_shift + 1)
        elif self.decoder.current_cipher == "Rail Fence":
            if minus_btn.collidepoint(pos):
                self.decoder.rail_fence_rails = max(2, self.decoder.rail_fence_rails - 1)
            elif plus_btn.collidepoint(pos):
                self.decoder.rail_fence_rails = min(10, self.decoder.rail_fence_rails + 1)

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
        
        # Display current challenge description with text wrapping
        challenge_text = self.challenges[self.current_challenge_index]["description"]
        wrapped_challenge = wrap_text(challenge_text, FONT, 700)
        for i, line in enumerate(wrapped_challenge):
            desc_text = FONT.render(line, True, DARK_TEXT)
            screen.blit(desc_text, (50, 100 + (i * 40)))

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

        # Render hint if active with text wrapping
        if self.show_hint:
            wrapped_hint = wrap_text(self.challenges[self.current_challenge_index]["hint"], FONT, 500)
            for i, line in enumerate(wrapped_hint):
                hint_surface = FONT.render(line, True, GREEN)
                screen.blit(hint_surface, (200, 500 + (i * 40)))

        # Automatically populate decoder input with current challenge
        self.decoder.input_text = self.challenges[self.current_challenge_index]["description"].split(": ")[1]
        self.decoder.output_text = self.decoder.decode(self.decoder.input_text)
        
        # Draw decoder panel and unpack all three returned values
        decoder_input_box, cipher_buttons, parameter_buttons = self.decoder.draw(screen)

        return input_box, check_button, hint_button, decoder_input_box, cipher_buttons, parameter_buttons
    
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
                        # Unpack all values returned by draw_challenge_screen
                        input_box, check_button, hint_button, decoder_input_box, cipher_buttons, parameter_buttons = self.draw_challenge_screen()
                        
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
                        
                        # Handle parameter buttons
                        if parameter_buttons[0] is not None and parameter_buttons[1] is not None:
                            self.handle_parameter_buttons(event.pos, parameter_buttons)

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
        if ((self.user_input.upper() == self.challenges[self.current_challenge_index]["solution"]) or (self.user_input.lower() == self.challenges[self.current_challenge_index]["solution"])):
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