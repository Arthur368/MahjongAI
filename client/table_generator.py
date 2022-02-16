import numpy as np
import random

from mahjong_tile import Tile
from mahjong_patition import Partition
used = np.zeros(34)


def comb(n, r, rep):
    if r == 0:
        hand = []
        card_idx = 0
        for num_of_card in used:
            for i in range(int(num_of_card)):
                hand.append(card_idx)
            card_idx += 1
        #hand_str = Tile.tiles34_to_string(hand)
        shanten = Partition.shantin_normal(hand, [])
        print(shanten)
    else:
        for i in range(rep + 1):
            if r - i >= 0:
                used[n-1] += i
                if n > 0:
                    comb(n - 1, r - i, rep)
                used[n-1] -= i

#comb(34, 14, 4)

# This func aims to encode a hand into a sequence with number of cards and their "distances",
# e.g (12m -> 111, 13m -> 121, 14m -> 1|1) and then calculate shanten number.
def encode_tile34(tile34):
    last_card = -1
    encoded_str = ""
    num_of_card = 0
    for t in tile34:        
        if t != last_card:
            if tile34.index(t) != 0:
                encoded_str += str(num_of_card)
                if t - last_card >= 3 or t//9 != last_card//9 or t >= 27 or last_card >= 27:
                    encoded_str += "|"
                elif t - last_card == 2:
                    encoded_str += "2"
                else:
                    encoded_str += "1"
                if tile34.index(t) == len(tile34) - 1:
                    encoded_str += "1"
                num_of_card = 1
            else:
                num_of_card += 1

            last_card = t
        else:
            num_of_card += 1
            if tile34.index(t) == -1:
                encoded_str += str(num_of_card)

    # Normalize the encoded str
    list_of_blocks = sorted(encoded_str.split("|"), reverse = True)
    normalized_str = ""

    for block in list_of_blocks:
        if int("".join(reversed(block))) > int(block):
            block = reversed(block)
        
        normalized_str += block
        if list_of_blocks.index(block) != len(list_of_blocks) - 1:
            normalized_str += "|"



    return normalized_str

yama = np.ones(136)

hand = []
while len(hand) < 14:
    card = random.randint(0, 135)
    if yama[card] > 0:
        hand.append(card//4)
        yama[card] -= 1
hand = sorted(hand)

print(Tile.tiles34_to_string(hand))
print(encode_tile34(hand))
            
        


    
    