import pygame
import random
import collections
import time

# Initialize Pygame
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Blackjack Trainer")
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Card representations
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# Basic strategy dictionaries (H17, 6-deck, late surrender)
surrender_rules = {
    15: {10: 'R'},
    16: {9: 'R', 10: 'R', 'A': 'R'},
    17: {'A': 'R'}
}

split_rules = {
    '2': {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P'},
    '3': {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P'},
    '4': {5: 'P', 6: 'P'},
    '5': {2: 'D', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'D', 8: 'D', 9: 'D'},
    '6': {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P'},
    '7': {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P'},
    '8': {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 8: 'P', 9: 'P', 10: 'P', 'A': 'P'},
    '9': {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 8: 'P', 9: 'P'},
    '10': {},
    'A': {2: 'P', 3: 'P', 4: 'P', 5: 'P', 6: 'P', 7: 'P', 8: 'P', 9: 'P', 10: 'P', 'A': 'P'}
}

soft_rules = {
    13: {5: 'D', 6: 'D'},
    14: {5: 'D', 6: 'D'},
    15: {4: 'D', 5: 'D', 6: 'D'},
    16: {4: 'D', 5: 'D', 6: 'D'},
    17: {3: 'D', 4: 'D', 5: 'D', 6: 'D'},
    18: {2: 'Ds', 3: 'Ds', 4: 'Ds', 5: 'Ds', 6: 'Ds', 9: 'H', 10: 'H', 'A': 'H'},
    19: {6: 'Ds'},
    20: {}
}

hard_rules = {
    8: {},
    9: {3: 'D', 4: 'D', 5: 'D', 6: 'D'},
    10: {2: 'D', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'D', 8: 'D', 9: 'D'},
    11: {2: 'D', 3: 'D', 4: 'D', 5: 'D', 6: 'D', 7: 'D', 8: 'D', 9: 'D', 10: 'D', 'A': 'D'},
    12: {4: 'S', 5: 'S', 6: 'S'},
    13: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S'},
    14: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S'},
    15: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S'},
    16: {2: 'S', 3: 'S', 4: 'S', 5: 'S', 6: 'S'},
    17: {}
}

# Normalize dealer upcard
def normalize_card(card):
    rank = card[:-1]
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 'A'
    else:
        return int(rank)

# Get card value
def card_value(card):
    rank = card[:-1]
    if rank in ['J', 'Q', 'K', '10']:
        return 10
    elif rank == 'A':
        return 11
    else:
        return int(rank)

# Calculate hand value
def hand_value(hand):
    val = 0
    aces = 0
    for card in hand:
        v = card_value(card)
        if v == 11:
            aces += 1
        val += v
    while val > 21 and aces:
        val -= 10
        aces -= 1
    return val, aces > 0

# Get basic strategy decision
def get_strategy(player_hand, dealer_up, can_split, can_double, can_surrender, split_count=0):
    p_val, is_soft = hand_value(player_hand)
    dealer = normalize_card(dealer_up)
    
    # SURRENDER FIRST (highest priority)
    if can_surrender and len(player_hand) == 2 and not is_soft:
        if p_val in surrender_rules and dealer in surrender_rules[p_val]:
            return 'R'
    
    # Split if pair
    if can_split and len(player_hand) == 2 and player_hand[0][:-1] == player_hand[1][:-1] and split_count < 3:
        pair_rank = player_hand[0][:-1]
        if pair_rank in ['J', 'Q', 'K']:
            pair_rank = '10'
        if pair_rank in split_rules and dealer in split_rules[pair_rank]:
            action = split_rules[pair_rank][dealer]
            if pair_rank == '5':
                return 'D' if can_double else 'H'
            if action == 'P':
                return 'P'
    
    # Soft hands
    if is_soft and p_val <= 20:
        if p_val in soft_rules and dealer in soft_rules[p_val]:
            action = soft_rules[p_val][dealer]
            if action == 'D' or action == 'Ds':
                return 'D' if can_double else ('S' if action == 'Ds' else 'H')
            return action
        return 'H' if p_val <= 17 else 'S'
    
    # Hard hands
    if p_val <= 8:
        return 'H'
    if p_val >= 17:
        return 'S'
    if p_val in hard_rules and dealer in hard_rules[p_val]:
        action = hard_rules[p_val][dealer]
        if action == 'D':
            return 'D' if can_double else 'H'
        return action
    return 'H'

# Draw text
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Button class
class Button:
    def __init__(self, text, x, y, action):
        self.text = text
        self.rect = pygame.Rect(x, y, 100, 50)
        self.action = action

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)
        draw_text(self.text, small_font, WHITE, self.rect.x + 10, self.rect.y + 10)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

# Main game logic
def main():
    clock = pygame.time.Clock()
    deck = [rank + suit for suit in SUITS for rank in RANKS] * 6
    random.shuffle(deck)
    
    error_queue = collections.deque()
    hands_played_since_error = 0
    
    while True:
        if len(deck) < 52:
            deck = [rank + suit for suit in SUITS for rank in RANKS] * 6
            random.shuffle(deck)
        
        # Check for replay
        is_replay = False
        if error_queue and hands_played_since_error >= 20:
            replay_hand, replay_dealer, replay_correct = error_queue.popleft()
            hands_played_since_error = 0
            is_replay = True
            
            current_hands = [replay_hand[:]]
            dealer_up = replay_dealer
            splits = 0
            
            screen.fill(GREEN)
            draw_text("REPLAYING MISTAKE!", font, RED, 200, 50)
            pygame.display.flip()
            time.sleep(2)
        else:
            # Deal new hand with bias
            attempts = 0
            while attempts < 10:
                player_hand = [deck.pop(), deck.pop()]
                dealer_up = deck.pop()
                p_val, is_soft = hand_value(player_hand)
                is_pair = player_hand[0][:-1] == player_hand[1][:-1]
                if is_soft or is_pair or random.random() < 0.4:
                    break
                deck.extend(player_hand + [dealer_up])
                random.shuffle(deck)
                attempts += 1
            
            current_hands = [player_hand]
            splits = 0
        
        hand_results = [None] * len(current_hands)
        mistake_in_game = False
        
        # Play hands IN STRICT NUMERIC ORDER (1, 2, 3, 4)
        i = 0  # Current hand index
        while i < len(current_hands):
            hand_idx = i
            hand = current_hands[hand_idx]
            
            # Play THIS hand completely
            while hand_results[hand_idx] is None:
                p_val, is_soft = hand_value(hand)
                
                if p_val > 21:
                    hand_results[hand_idx] = "Bust"
                    break
                
                # Determine available actions
                can_split = (len(hand) == 2 and hand[0][:-1] == hand[1][:-1] and splits < 3)
                can_double = (len(hand) == 2)
                can_surrender = (len(hand) == 2 and hand_idx == 0 and splits == 0)
                
                correct_action = get_strategy(hand, dealer_up, can_split, can_double, can_surrender, splits)
                
                # Show buttons
                buttons = [
                    Button("Hit", 50, 500, 'H'),
                    Button("Stand", 160, 500, 'S')
                ]
                if can_double:
                    buttons.append(Button("Double", 270, 500, 'D'))
                if can_split:
                    buttons.append(Button("Split", 380, 500, 'P'))
                if can_surrender:
                    buttons.append(Button("Surrender", 490, 500, 'R'))
                
                # Get player choice
                chosen = None
                while not chosen:
                    screen.fill(GREEN)
                    draw_text("Dealer: " + dealer_up, font, BLACK, 350, 100)
                    
                    # Display ALL hands, highlight CURRENT hand
                    y = 200
                    for j, h in enumerate(current_hands):
                        color = RED if j == hand_idx else BLACK
                        hand_str = ' '.join(h)
                        draw_text(f"Hand {j+1}: {hand_str}", font, color, 150, y)
                        if hand_results[j]:
                            draw_text(f"({hand_results[j]})", small_font, color, 550, y)
                        y += 50
                    
                    for btn in buttons:
                        btn.draw()
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            return
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            for btn in buttons:
                                if btn.clicked(event.pos):
                                    chosen = btn.action
                                    break
                    
                    pygame.display.flip()
                    clock.tick(30)
                
                # Check for mistake
                if chosen != correct_action and not is_replay:
                    mistake_in_game = True
                    error_queue.append((hand[:], dealer_up, correct_action))
                    hands_played_since_error = 0
                    
                    # Show mistake
                    screen.fill(GREEN)
                    draw_text("MISTAKE!", font, RED, 300, 150)
                    draw_text(f"Hand {hand_idx+1}: {' '.join(hand)}", font, BLACK, 200, 200)
                    draw_text(f"Dealer: {dealer_up}", font, BLACK, 300, 250)
                    draw_text(f"Correct: {correct_action}", font, RED, 250, 300)
                    
                    waiting = True
                    while waiting:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                pygame.quit()
                                return
                            if event.type == pygame.MOUSEBUTTONDOWN:
                                waiting = False
                        pygame.display.flip()
                        clock.tick(30)
                    
                    # Play correct action
                    chosen = correct_action
                    time.sleep(1)
                
                # Execute action
                if chosen == 'R':
                    hand_results[hand_idx] = "Surrender"
                elif chosen == 'S':
                    hand_results[hand_idx] = p_val
                elif chosen == 'D':
                    hand.append(deck.pop())
                    p_val, _ = hand_value(hand)
                    hand_results[hand_idx] = p_val if p_val <= 21 else "Bust"
                elif chosen == 'P':
                    # FIXED SPLIT: Deal cards FIRST, THEN replace hand
                    splits += 1
                    card1 = deck.pop()  # Card for hand 1
                    card2 = deck.pop()  # Card for hand 2
                    
                    new_hand1 = [hand[0], card1]
                    new_hand2 = [hand[1], card2]
                    
                    # Replace current hand with TWO new hands AT SAME POSITION
                    current_hands[hand_idx:hand_idx+1] = [new_hand1, new_hand2]
                    hand_results[hand_idx:hand_idx+1] = [None, None]
                    
                    # DO NOT increment i - stay to play first new hand
                    break
                elif chosen == 'H':
                    hand.append(deck.pop())
                
                if not mistake_in_game:
                    hands_played_since_error += 1
            
            i += 1
        
        # Dealer play
        dealer_hand = [dealer_up, deck.pop()]
        while hand_value(dealer_hand)[0] < 17 or (hand_value(dealer_hand)[0] == 17 and hand_value(dealer_hand)[1]):
            dealer_hand.append(deck.pop())
        dealer_val = hand_value(dealer_hand)[0]
        
        # Show final results
        next_button = Button("Next Hand", 350, 500, 'next')
        waiting = True
        while waiting:
            screen.fill(GREEN)
            draw_text("FINAL RESULTS", font, BLACK, 300, 50)
            draw_text(f"Dealer: {' '.join(dealer_hand)} ({dealer_val})", font, BLACK, 150, 100)
            
            y = 150
            for i, result in enumerate(hand_results):
                draw_text(f"Hand {i+1}: {result}", font, BLACK, 150, y)
                y += 50
            
            next_button.draw()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if next_button.clicked(event.pos):
                        waiting = False
            
            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    main()
