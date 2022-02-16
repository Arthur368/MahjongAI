from copy import deepcopy
import numpy as np
import random

from numpy.core.fromnumeric import partition
from mahjong_tile import Tile

class divided_result:
    
    def __init__(self, original, cotsu, shuntsu, tuitsu, taatsu, other):
        self.original = original # original hand in tile34 form
        self.cotsu = cotsu
        self.shuntsu = shuntsu
        self.tuitsu = tuitsu
        self.taatsu = taatsu
        self.other = other
        self.shanten = self.shanten_calc

    @property
    def shanten_calc(self):
        # calc shanten for koukushi
        onenine = 0
        have_onenine_pair = False
        types = set(self.original)
        
        for t in types:
            if t in Tile.ONENINE:
                if self.original.count(t) >= 2:
                    have_onenine_pair = True
                
                onenine += 1
        
        shanten_koukushi = 13 - onenine - int(have_onenine_pair)
        
        # then calc shanten for chituitsu(7-pairs)
        pairs = len(self.tuitsu)
        shanten_chitui = 6 - pairs

        # then for normal
        groups = len(self.shuntsu) + len(self.cotsu)
        taatsu = len(self.taatsu)

        #shanten = 8 - 2 * groups - max(pairs + taatsu, len(self.original)//3-groups) - min(1, max(0, pairs + taatsu - (4 - groups)))
        shanten = 8 - 2 * groups - min(pairs + taatsu, 5 - groups)
        real_shanten = min(shanten, shanten_chitui, shanten_koukushi)

        return real_shanten




#result = hand_breaker([1,2,3,4,5,6,6,8,11,12,15,15,31,32])
#print(result.cotsu,result.shuntsu,result.tuitsu,result.tatsu,result.other)

def t_34_to_matrix(tiles34):
    encoded_matrix = np.zeros((4,9))
    
    for t in tiles34:
        encoded_matrix[t//9][t%9] += 1

    return encoded_matrix

def hand_breaker(tiles34):
    # using 5-block theory to divide the hand into mentsu,tatsu and singles

    # encode tiles to matrix
    tiles_matrix = t_34_to_matrix(tiles34)
    tiles_matrixcpy1 = deepcopy(tiles_matrix)
    tiles34cpy2 = deepcopy(tiles_matrix)
    cstto_ls = [[],[],[],[],[]]
    # cotsu first
    for i in range(4):
        for j in range(9):
            if tiles_matrixcpy1[i][j] >= 3:
                tiles_matrixcpy1[i][j] -= 3
                cstto_ls[0].append(9*i + j)
    # shuntsu second
    for i in range(4):
        if i < 3:
            for j in range(9):
                if j <= 6:
                    while tiles_matrixcpy1[i][j] >= 1 and tiles_matrixcpy1[i][j+1] >= 1 and tiles_matrixcpy1[i][j+2] >=1:
                        tiles_matrixcpy1[i][j] -= 1
                        tiles_matrixcpy1[i][j+1] -= 1
                        tiles_matrixcpy1[i][j+2] -= 1
                        cstto_ls[1].append(9*i + j)
                    

    # tuitsu next
    for i in range(4):
        for j in range(9):
            if tiles_matrixcpy1[i][j] >= 2:
                tiles_matrixcpy1[i][j] -= 2
                cstto_ls[2].append(9*i + j)
    # tatsu
    for i in range(4):
        if i < 3:
            for j in range(9):
                if j <= 6:
                    if tiles_matrixcpy1[i][j] >= 1: 
                        if tiles_matrixcpy1[i][j+1] >= 1:
                            tiles_matrixcpy1[i][j] -= 1
                            tiles_matrixcpy1[i][j+1] -= 1
                            cstto_ls[3].append((9*i + j, 9*i + j + 1))

                        elif tiles_matrixcpy1[i][j+2] >= 1:
                            tiles_matrixcpy1[i][j] -= 1
                            tiles_matrixcpy1[i][j+2] -= 1
                            cstto_ls[3].append((9*i + j, 9*i + j + 2))

    # singles
    for i in range(4):
        for j in range(9):
            if tiles_matrixcpy1[i][j] >= 1:
                cstto_ls[4].append(9*i + j)

    result = divided_result(tiles34,cstto_ls[0],cstto_ls[1],cstto_ls[2],cstto_ls[3],cstto_ls[4])

    return result

yama = np.ones(136)

hand = []
while len(hand) < 14:
    card = random.randint(0, 35)
    if yama[card] > 0:
        hand.append(card//4)
        yama[card] -= 1
hand = sorted(hand)   
#hand = [0,1,2,3,4,5,6,7,8,12,13,20,21,30]     
print(hand)

"""r = hand_breaker(hand)


#print(r.cotsu, r.shuntsu, r.tuitsu, r.tatsu, r.other)
print(Tile.tiles34_to_string(hand))
print(r.shanten)"""

class Partition:

    @staticmethod
    def _partition_single_type(tiles34):
        """
        Partition tiles of one type into melds, half-finished melds and singles
        :param tiles34: tiles of the same type
        :return: a list of multiple partition results, each partition result is a list of list, where each list in a
        partition represents a partitioned component
        """
        len_t = len(tiles34)

        # no tiles of this type
        if len_t == 0:
            return [[]]
        # one tile, or two tile which can be parsed into an open set
        if len_t == 1 or (len_t == 2 and abs(tiles34[0] - tiles34[1]) < 3):
            return [[tiles34]]
        # two separate tiles
        if len_t == 2:
            return [[tiles34[0:1], tiles34[1:2]]]

        res = []

        # parse a pon meld
        if tiles34[0] == tiles34[1] == tiles34[2]:
            tmp_res = Partition._partition_single_type(tiles34[3:])
            if len(tmp_res) > 0:
                for tile_set in tmp_res:
                    res.append([tiles34[0:3]] + tile_set)

        # parse a chow meld
        if tiles34[0] + 1 in tiles34 and tiles34[0] + 2 in tiles34:
            rec_tiles = deepcopy(tiles34)
            rec_tiles.remove(tiles34[0])
            rec_tiles.remove(tiles34[0] + 1)
            rec_tiles.remove(tiles34[0] + 2)
            tmp_res = Partition._partition_single_type(rec_tiles)
            if len(tmp_res) > 0:
                for tile_set in tmp_res:
                    res.append([[tiles34[0], tiles34[0] + 1, tiles34[0] + 2]] + tile_set)

        # parse an two-headed half-finished meld
        if tiles34[0] + 1 in tiles34:
            rec_tiles = deepcopy(tiles34)
            rec_tiles.remove(tiles34[0])
            rec_tiles.remove(tiles34[0] + 1)
            tmp_res = Partition._partition_single_type(rec_tiles)
            if len(tmp_res) > 0:
                for tile_set in tmp_res:
                    res.append([[tiles34[0], tiles34[0] + 1]] + tile_set)

        # parse an dead half-finished meld
        if tiles34[0] + 2 in tiles34:
            rec_tiles = deepcopy(tiles34)
            rec_tiles.remove(tiles34[0])
            rec_tiles.remove(tiles34[0] + 2)
            tmp_res = Partition._partition_single_type(rec_tiles)
            if len(tmp_res) > 0:
                for tile_set in tmp_res:
                    res.append([[tiles34[0], tiles34[0] + 2]] + tile_set)

        # parse a pair
        if tiles34[0] == tiles34[1]:
            tmp_res = Partition._partition_single_type(tiles34[2:])
            if len(tmp_res) > 0:
                for tile_set in tmp_res:
                    res.append([tiles34[0:2]] + tile_set)

        tmp_res = Partition._partition_single_type(tiles34[1:])
        if len(tmp_res) > 0:
            for tile_set in tmp_res:
                res.append([tiles34[0:1]] + tile_set)

        tuned_res = []
        min_len = min([len(p) for p in res])
        for p in res:
            if len(p) <= min_len and p not in tuned_res:
                tuned_res.append(p)

        return tuned_res

    @staticmethod
    def partition(tiles34):
        """
        Partition a set of tiles in 34-form into finished melds, half-finished melds and singles.
        :param tiles34:
            a list of tiles in 34-form
        :return:
            a list of partition results of the input tiles, each partition is a list of list,
            where each list represents a partitioned component
        """
        p_man = Partition._partition_single_type([t for t in tiles34 if 0 <= t < 9])
        p_pin = Partition._partition_single_type([t for t in tiles34 if 9 <= t < 18])
        p_suo = Partition._partition_single_type([t for t in tiles34 if 18 <= t < 27])
        h_chr = [t for t in tiles34 if 27 <= t < 34]
        p_chr = [[[chr_tile] * h_chr.count(chr_tile) for chr_tile in set(h_chr)]]
        res = []
        for pm in p_man:
            for pp in p_pin:
                for ps in p_suo:
                    for pc in p_chr:
                        res.append(pm + pp + ps + pc)
        return res

    @staticmethod
    def partition_winning_tiles(hand34, final_tile):
        hand_total = hand34 + [final_tile]
        hand_total_set = set(hand_total)
        res = []

    @staticmethod
    def _shantin_normal(partitions, called_meld_num):

        def geo_vec_normal(p):
            geo_vec = [0] * 6

            def incre(set_type):
                geo_vec[set_type] += 1

            for m in p:
                len(m) == 1 and incre(0)
                len(m) == 2 and abs(m[0] - m[1]) == 0 and incre(3)
                len(m) == 2 and abs(m[0] - m[1]) == 1 and incre(2 if m[0] % 9 > 0 and m[1] % 9 < 8 else 1)
                len(m) == 2 and abs(m[0] - m[1]) == 2 and incre(1)
                len(m) == 3 and incre(5 if m[0] == m[1] else 4)

            return geo_vec

        def shantin_n(p):
            geo_vec = geo_vec_normal(p)
            needed_set = (4 - called_meld_num) - geo_vec[4] - geo_vec[5]
            if geo_vec[3] > 0:
                if geo_vec[1] + geo_vec[2] + geo_vec[3] - 1 >= needed_set:
                    return needed_set - 1
                else:
                    return 2 * needed_set - (geo_vec[1] + geo_vec[2] + geo_vec[3] - 1) - 1
            else:
                if geo_vec[1] + geo_vec[2] >= needed_set:
                    return needed_set
                else:
                    return 2 * needed_set - (geo_vec[1] + geo_vec[2])

        return min([shantin_n(p) for p in partitions])

    @staticmethod
    def shantin_normal(tiles34, called_melds):
        """
        Calculate the normal shantin of a list of tiles.
        Normal shantin means that there is no any extra constraint on the winning tiles' pattern.
        :param tiles34:
            a list of tiles in 34-form, normally it is meant to be the tiles in hand
        :param called_melds:
            the ever called melds
        :return:
            the normal shantin.
        """
        return Partition._shantin_normal(Partition.partition(tiles34), len(called_melds))


print(Partition.partition(hand))
print(Partition.shantin_normal(hand, []))
print(Tile.tiles34_to_string(hand))

# This func is for calc card which can decrese shanten number
def waiting_card_calc(hand):
    for i in range(34):
        hand.append(i)
        hand = sorted(hand)
        
