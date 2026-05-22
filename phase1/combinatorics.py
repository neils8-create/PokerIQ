def factorial(n):
    result = 1
    i = 1
    while i <= n:
        result = result * i
        i = i + 1
    return result

def C(n, k):
    result = factorial(n)//(factorial(k) * factorial(n-k))
    return result

def build_deck():
    deck = []
    suits = ['s', 'h', 'd', 'c']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'] 

    for suit in suits:
        for rank in ranks:
            card = rank + suit
            deck.append(card)
    return deck

def deal_hole_cards(deck, card1, card2):
    remaining_deck = deck.copy()
    hole_cards = [card1, card2]
    for card in hole_cards:
        if card in deck:
            remaining_deck.remove(card)      
    return hole_cards, remaining_deck
    
deck = build_deck()
hole_cards, remaining_deck = deal_hole_cards(deck, "Ks", "Kh")
print(hole_cards)
print(len(remaining_deck))

    

print(C(52, 2))
print(C(52, 5))
print(C(50, 5))


