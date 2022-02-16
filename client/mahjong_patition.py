import json
import random
from copy import deepcopy

#from client.mahjong_tile import Tile
from mahjong_tile import Tile

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

    @staticmethod
    def _shantin_pinhu(partitions, called_meld_num, bonus_chrs):
        if called_meld_num:
            return 10

        def geo_vec_pinhu(p):
            geo_vec = [0] * 6

            def incre(set_type):
                geo_vec[set_type] += 1

            for m in p:
                len(m) == 1 and incre(0)
                len(m) == 2 and abs(m[0] - m[1]) == 0 and m[0] not in bonus_chrs and incre(3)
                len(m) == 2 and abs(m[0] - m[1]) == 1 and incre(2 if m[0] % 9 > 0 and m[1] % 9 < 8 else 1)
                len(m) == 2 and abs(m[0] - m[1]) == 2 and incre(1)
                len(m) == 3 and incre(5 if m[0] == m[1] else 4)

            return geo_vec

        def shantin_ph(p):
            geo = geo_vec_pinhu(p)
            need_chow = 4 - geo[4]
            if geo[1] + geo[2] >= need_chow:
                return (geo[3] == 0) + need_chow - 1 + (geo[2] == 0)
            else:
                return (geo[3] == 0) + need_chow - 1 + need_chow - geo[1] - geo[2]

        return min(shantin_ph(p) for p in partitions)

    @staticmethod
    def shantin_no_triplets(tiles34, called_melds, bonus_chrs):
        """
        Calculate the shantin of reaching a "no triplets" waiting hand.
        (1) A "No triplets" hand means the expected winning hand tiles has no pons(triplets)
        (2) There can be only chows(sequences),
        (3) The pair should not be any kind of bonus character tiles!
        :param tiles34:
            A list of tiles in 34-form, usually the tiles in hand
        :param called_melds:
            The ever called melds.
            When any kind of meld if called, the form "pinhu" is not any more constructable
        :param bonus_chrs:
            A list of character tiles that are the bot's yaki tiles
        :return:
            The shantin of "No triplets" form
        """
        partitions = Partition.partition(tiles34)
        return Partition._shantin_pinhu(partitions, len(called_melds), bonus_chrs)

    @staticmethod
    def _shantin_no19(partitions, called_melds):
        for m in called_melds:
            if any(tile in Tile.ONENINE for tile in m):
                return 10

        def geo_vec_no19(p):
            geo_vec = [0] * 6

            def incre(set_type):
                geo_vec[set_type] += 1

            for m in p:
                if m[0] > 26:
                    continue
                len(m) == 1 and 0 < m[0] % 9 < 8 and incre(0)
                len(m) == 2 and abs(m[0] - m[1]) == 0 and 0 < m[0] % 9 < 8 and incre(3)
                len(m) == 2 and abs(m[0] - m[1]) == 1 and m[0] % 9 > 1 and m[1] % 9 < 7 and incre(2)
                len(m) == 2 and abs(m[0] - m[1]) == 1 and (m[0] % 9 == 1 or m[1] % 9 == 7) and incre(1)
                len(m) == 2 and abs(m[0] - m[1]) == 2 and m[0] % 9 > 0 and m[1] % 9 < 8 and incre(1)
                len(m) == 3 and m[0] == m[1] and 0 < m[0] % 9 < 8 and incre(5)
                len(m) == 3 and m[0] != m[1] and incre(4 if m[0] % 9 > 0 and m[2] % 9 < 8 else 1)

            return geo_vec

        def shantin_no19(p):
            geo_vec = geo_vec_no19(p)
            needed_set = (4 - len(called_melds)) - geo_vec[4] - geo_vec[5]
            if geo_vec[3] > 0:
                if geo_vec[1] + geo_vec[2] + geo_vec[3] - 1 >= needed_set:
                    return needed_set - 1
                else:
                    need_single = needed_set - (geo_vec[1] + geo_vec[2] + geo_vec[3] - 1)
                    if geo_vec[0] >= need_single:
                        return 2 * needed_set - (geo_vec[1] + geo_vec[2] + geo_vec[3] - 1) - 1
                    else:
                        return 2 * needed_set - (geo_vec[1] + geo_vec[2] + geo_vec[3] - 1) - 1 + need_single - geo_vec[
                            0]
            else:
                if geo_vec[1] + geo_vec[2] >= needed_set:
                    return needed_set + (geo_vec[0] == 0)
                else:
                    need_single = needed_set - (geo_vec[1] + geo_vec[2]) + 1
                    if geo_vec[0] >= need_single:
                        return 2 * needed_set - (geo_vec[1] + geo_vec[2])
                    else:
                        return 2 * needed_set - (geo_vec[1] + geo_vec[2]) + need_single - geo_vec[0]

        return min(shantin_no19(p) for p in partitions)

    @staticmethod
    def shantin_no_19(tiles34, called_melds):
        """
        Calculate the shantin of "no19" form.
        A "no19" hand mean the expected winning hand tiles only contain tiles from number 2 to 8.
        :param tiles34:
            A list of tiles in 34-form, usually the tiles in hand
        :param called_melds:
            The ever called melds
        :return:
            The shantin of no19 form
        """
        partitions = Partition.partition(tiles34)
        return Partition._shantin_no19(partitions, called_melds)

    @staticmethod
    def shantin_no_sequences(tiles34, called_melds):
        """
        Calculate the shantin of "No sequence" form.
        A "No sequence" from means that the expected winning tiles has no chow(sequence) melds
        :param tiles34:
            A list of tiles in 34-form, usually the hand tiles
        :param called_melds:
            The ever called melds
        :return:
            The shantin of pph form
        """
        if any(len(m) > 1 and m[0] != m[1] for m in called_melds):
            return 10
        num_kezi = len([tile for tile in set(tiles34) if tiles34.count(tile) == 3])
        num_pair = len([tile for tile in set(tiles34) if tiles34.count(tile) == 2])
        need_kezi = 4 - len(called_melds) - num_kezi
        return (need_kezi - 1) if (num_pair >= need_kezi + 1) else (2 * need_kezi - num_pair)

    @staticmethod
    def shantin_seven_pairs(tiles34, called_melds):
        """
        Calculate shantin of form "Seven pairs".
        A "Seven pairs" form means the expected winning tiles are 7 pairs
        :param tiles34:
            A list of tiles in 34-form, usually the hand tiles
        :param called_melds:
            The ever called melds
        :return:
            The shantin of form "Seven pairs"
        """
        if len(called_melds) > 0:
            return 10
        else:
            num_pair = len([tile for tile in set(tiles34) if tiles34.count(tile) >= 2])
            return 6 - num_pair

    @staticmethod
    def _shantin_pure_color(tiles34, called_melds, partitions):
        qh_type = []

        if len(called_melds) > 0:
            meld_types = []
            for m in called_melds:
                if m[0] // 9 == 3:
                    continue
                if m[0] // 9 not in meld_types:
                    meld_types.append(m[0] // 9)
            if len(meld_types) > 1:
                return 10
            else:
                qh_type = meld_types

        if (len(qh_type) == 0 and len(called_melds) > 0) or len(called_melds) == 0:
            type_geo = [
                len([t for t in tiles34 if 0 <= t < 9]),
                len([t for t in tiles34 if 9 <= t < 18]),
                len([t for t in tiles34 if 18 <= t < 27])
            ]
            max_num = max(type_geo)
            qh_type = [i for i in range(3) if type_geo[i] == max_num]

        if len(qh_type) == 0:
            return 10

        def geo_vec_qh(p, tp):
            allowed_types = [tp, 3]
            geo_vec = [0] * 6

            def incre(set_type):
                geo_vec[set_type] += 1

            for m in p:
                if m[0] // 9 in allowed_types:
                    len(m) == 1 and incre(0)
                    len(m) == 2 and abs(m[0] - m[1]) == 0 and incre(3)
                    len(m) == 2 and abs(m[0] - m[1]) == 1 and incre(2 if m[0] % 9 > 0 and m[1] % 9 < 8 else 1)
                    len(m) == 2 and abs(m[0] - m[1]) == 2 and incre(1)
                    len(m) == 3 and incre(5 if m[0] == m[1] else 4)
            return geo_vec

        def shantin_n(p, tp):
            geo_vec = geo_vec_qh(p, tp)
            # print(geo_vec)
            s, p, o, f = geo_vec[0], geo_vec[3], geo_vec[1] + geo_vec[2], geo_vec[4] + geo_vec[5]
            if p > 0:
                p -= 1
                st = 0
                needed_set = 3 - len(called_melds) - f
                while needed_set > 0:
                    if o > 0:
                        needed_set, o, st = needed_set - 1, o - 1, st + 1
                    elif p > 0:
                        needed_set, p, st = needed_set - 1, p - 1, st + 1
                    elif s > 0:
                        needed_set, st, s = needed_set - 1, st + 2, s - 1
                    else:
                        needed_set, st = needed_set - 1, st + 3
                return st if (o + p) > 0 else (st + 1 if s > 0 else st + 2)
            else:
                st = 0
                needed_set = 4 - len(called_melds) - f
                while needed_set > 0:
                    if o > 0:
                        needed_set, o, st = needed_set - 1, o - 1, st + 1
                    elif s > 0:
                        needed_set, st, s = needed_set - 1, st + 2, s - 1
                    else:
                        needed_set, st = needed_set - 1, st + 3
                return st if s > 0 else st + 1

        def shantin_qh(p):
            return min([shantin_n(p, t) for t in qh_type])

        return min([shantin_qh(p) for p in partitions])

    @staticmethod
    def shantin_pure_color(tiles34, called_melds):
        """
        Calculate the shantin of "pure color" form.
        A "pure color" form means the expected winning tiles contain only character tiles and one other type of tiles.
        :param tiles34:
            A list of tiles in 34-form
        :param called_melds:
            The ever called melds
        :return:
            The shantin of "pure color"
        """
        partitions = Partition.partition(tiles34)
        return Partition._shantin_pure_color(tiles34, called_melds, partitions)

    @staticmethod
    def shantin_multiple_forms(tiles34, called_melds, bonus_chrs):
        """
        Calculate shantin of different forms.
        It's an assemble of the various single shantin calculation function
        :param tiles34:
            A list of tiles in 34-form
        :param called_melds:
            The ever called melds
        :param bonus_chrs:
            A list of bonus character tiles
        :return:
            A dictionary, which has the special form name as key and the corresponding shantin as value
        """
        res = {}
        partitions = Partition.partition(tiles34)
        res["normal______"] = Partition._shantin_normal(partitions, len(called_melds))
        res["no_triplets_"] = Partition._shantin_pinhu(partitions, len(called_melds), bonus_chrs)
        res["no_19_______"] = Partition._shantin_no19(partitions, called_melds)
        res["no_sequences"] = Partition.shantin_no_sequences(tiles34, called_melds)
        res["seven_pairs_"] = Partition.shantin_seven_pairs(tiles34, called_melds)
        res["pure_color__"] = Partition._shantin_pure_color(tiles34, called_melds, partitions)
        return res
