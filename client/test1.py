from mahjong_tile import Tile
from copy import deepcopy

def cal_bonus_tiles(bonus_indicators_34):
    p1_dict = {8: 0, 17: 9, 26: 18, 30: 27, 33: 31}
    if isinstance(bonus_indicators_34, int):
        return [p1_dict.get(bonus_indicators_34, bonus_indicators_34 + 1)]
    if isinstance(bonus_indicators_34, list):
        res = []
        for b in bonus_indicators_34:
            res.append(p1_dict.get(b, b + 1))
        return res


def tiles34_to_string(tiles):
    tiles.sort()
    man = [t for t in tiles if t < 9]
    pin = [t - 9 for t in tiles if 9 <= t < 18]
    suo = [t - 18 for t in tiles if 18 <= t < 27]
    chr = [t - 27 for t in tiles if t >= 27]
    m = man and ''.join([str(m + 1) for m in man]) + 'm' or ''
    p = pin and ''.join([str(p + 1) for p in pin]) + 'p' or ''
    s = suo and ''.join([str(b + 1) for b in suo]) + 's' or ''
    z = chr and ''.join([str(ch + 1) for ch in chr]) + 'z' or ''
    return m + p + s + z

class WinCalc:
    def win_parse(hand34, final_tile):
        """
        To parse current hand tiles into melds which satisfies winning constrains
        :param hand34: tiles remaning in hand
        :param final_tile: the tile with which one finished his hand
        :return: list of list of list, different possibilities of partitioning total titles
        """
        hand_total = hand34 + [final_tile]
        hand_total_set = set(hand_total)
        res = []
        if all(hand_total.count(t) == 2 for t in hand_total_set) and len(hand_total) == 14:
                res.append([[t]*2 for t in hand_total_set])

        if all(t in hand_total for t in Tile.ONENINE) and all(t in Tile.ONENINE for t in hand_total):
            return [[[t]*hand_total.count(t) for t in Tile.ONENINE]]

        hand_total.sort()
        hand_man = [t for t in hand_total if t < 9]
        hand_pin = [t for t in hand_total if 9 <= t < 18]
        hand_suo = [t for t in hand_total if 18 <= t < 27]
        hand_chr = [t for t in hand_total if 27 <= t]
        man_parse = WinCalc._parse_nums(hand_man)
        pin_parse = WinCalc._parse_nums(hand_pin)
        suo_parse = WinCalc._parse_nums(hand_suo)
        chr_parse = WinCalc._parse_chrs(hand_chr)
        if hand_man and not man_parse:
            return res
        if hand_pin and not pin_parse:
            return res
        if hand_suo and not suo_parse:
            return res
        if hand_chr and not chr_parse:
            return res

        for a in man_parse:
            for b in pin_parse:
                for c in suo_parse:
                    res.append([m for m in a + b + c + chr_parse[0] if len(m) > 0])
        return res

    def _parse_nums(tiles):
        if len(tiles) == 0:
            return [[[]]]

        if len(tiles) == 1:
            return None

        if len(tiles) == 2:
            return [[tiles]] if tiles[0] == tiles[1] else None

        if len(tiles) == 3:
            ismeld = tiles[0] == tiles[1] == tiles[2] or (tiles[0] + 2) == (tiles[1] + 1) == tiles[2]
            return [[tiles]] if ismeld else None

        if len(tiles) % 3 == 1:
            return None

        res = []

        if len(tiles) % 3 == 2:
            if tiles[0] == tiles[1]:
                rec_res = WinCalc._parse_nums(tiles[2:])
                if rec_res:
                    for partition in rec_res:
                        res.append([tiles[0:2]] + partition)

        if tiles[0] == tiles[1] == tiles[2]:
            rec_res = WinCalc._parse_nums(tiles[3:])
            if rec_res:
                for partition in rec_res:
                    res.append([tiles[0:3]] + partition)

        if (tiles[0] + 1) in tiles and (tiles[0] + 2) in tiles:
            remain_tiles = deepcopy(tiles)
            remain_tiles.remove(tiles[0])
            remain_tiles.remove(tiles[0] + 1)
            remain_tiles.remove(tiles[0] + 2)
            rec_res = WinCalc._parse_nums(remain_tiles)
            if rec_res:
                for partition in rec_res:
                    res.append([[tiles[0], tiles[0] + 1, tiles[0] + 2]] + partition)

        return res if len(res) > 0 else None

    @staticmethod
    def _parse_chrs(tiles):
        if len(tiles) == 0:
            return [[]]

        if len(tiles) % 3 == 1 or any(tiles.count(t) == 1 for t in tiles):
            return None

        tiles_set = set(tiles)
        partition = [[t]*tiles.count(t) for t in tiles_set]

        return [partition] if len(partition) == (len(tiles) - 1) // 3 + 1 else None

#print(WinCalc.win_parse([1,2,7,7,7,9,10,11,20,21,22,30,30], 3))
#print(WinCalc.win_parse([0,1,1,2,2,12,12,13,13,14,14,33,33], 0))

from mahjong_tile import Tile
from copy import deepcopy

class WaitCalc:

    @staticmethod
    def waiting_calc(hand34):
        finished_hand = []
        win_tile = []

        def add_new_item(ppp, last_tile_):
            ppp = sorted(ppp, key=lambda x: x[0] + x[1] if len(x) > 1 else x[0])
            if ppp in finished_hand:
                index = finished_hand.index(ppp)
                win_tile[index].add(last_tile_)
            else:
                finished_hand.append(ppp)
                win_tile.append({last_tile_})

        was_seven_pairs = False

        if len(hand34) == 13:
            # check 7 pairs
            hand34_set = set(hand34)
            if len(hand34_set) == 7:
                pairs = [[t]*2 for t in hand34_set if hand34.count(t) == 2]
                single = [t for t in hand34_set if hand34.count(t) == 1]
                if len(pairs) == 6 and len(single) == 1:
                    pairs.append(single*2)
                    pairs = sorted(pairs, key=lambda x: x[0])
                    was_seven_pairs = True
                    add_new_item(pairs, single[0])
            # check guoshiwushuang
            if len(hand34_set) >= 12:
                metrics_19 = [hand34.count(t) for t in Tile.ONENINE]
                if metrics_19.count(1) == 13:
                    win_partition = [[t] for t in Tile.ONENINE]
                    for t in Tile.ONENINE:
                        tmp = win_partition
                        tmp[tmp.index([t])].append(t)
                        add_new_item(tmp, t)
                    return finished_hand, win_tile
                if metrics_19.count(1) == 11 and metrics_19.count(2) == 1:
                    waiting_tile = [t for t in Tile.ONENINE if t not in hand34_set][0]
                    win_partition = [[t]*hand34.count(t) for t in hand34]
                    win_partition.append([waiting_tile])
                    add_new_item(win_partition, waiting_tile)
                    return finished_hand, win_tile

        if len(hand34) == 1:
            add_new_item([hand34 * 2], hand34[0])
            return finished_hand, win_tile

        hand_man = [t for t in hand34 if t < 9]
        hand_pin = [t for t in hand34 if 9 <= t < 18]
        hand_suo = [t for t in hand34 if 18 <= t < 27]
        hand_chr = [t for t in hand34 if 27 <= t]
        wait_possible = WaitCalc._pruning_length(len(hand_man), len(hand_pin), len(hand_suo), len(hand_chr))
        if wait_possible:
            partitions = list()
            man_parse = WaitCalc._parse_num(hand_man) if len(hand_man) > 0 else [[]]
            pin_parse = WaitCalc._parse_num(hand_pin) if len(hand_pin) > 0 else [[]]
            suo_parse = WaitCalc._parse_num(hand_suo) if len(hand_suo) > 0 else [[]]
            chr_parse = WaitCalc._parse_chr(hand_chr) if len(hand_chr) > 0 else [[]]
            if (not man_parse and len(hand_man) > 0) or (not pin_parse and len(hand_pin) > 0) \
                    or (not suo_parse and len(hand_suo) > 0) or (not chr_parse and len(hand_chr) > 0):
                if was_seven_pairs:
                    return finished_hand, win_tile
                else:
                    return None, None
            for m in man_parse:
                for p in pin_parse:
                    for s in suo_parse:
                        for c in chr_parse:
                            partition = m + p + s + c
                            try:
                                partition = sorted(partition, key=lambda x: x[0] + x[1] if len(x) > 1 else x[0])
                            except:
                                print(partition)
                                return
                            if partition not in partitions:
                                partitions.append(partition)
            for p in partitions:
                pair_indices = [p.index(meld) for meld in p if len(meld) == 2 and meld[0] == meld[1]]
                open_indices = [p.index(meld) for meld in p if len(meld) == 2 and meld[0] != meld[1]]
                single_index = [p.index(meld) for meld in p if len(meld) == 1]

                if len(pair_indices) == 2 and len(open_indices) + len(single_index) == 0:
                    last_tile = p[pair_indices[0]][0]
                    tmp1 = deepcopy(p)
                    tmp1[pair_indices[0]].append(last_tile)
                    add_new_item(tmp1, last_tile)
                    last_tile = p[pair_indices[1]][0]
                    tmp2 = deepcopy(p)
                    tmp2[pair_indices[1]].append(last_tile)
                    add_new_item(tmp2, last_tile)

                if len(pair_indices) == 1 and len(open_indices) == 1 and len(single_index) == 0:
                    open_set = p[open_indices[0]]
                    open_index = open_indices[0]
                    if open_set[0] + 1 == open_set[1]:
                        if open_set[0] % 9 != 0:
                            tmp = deepcopy(p)
                            tmp[open_index].append(open_set[0] - 1)
                            tmp[open_index].sort()
                            add_new_item(tmp, open_set[0] - 1)
                        if open_set[1] % 9 != 8:
                            p[open_index].append(open_set[1] + 1)
                            add_new_item(p, open_set[1] + 1)
                    if open_set[0] + 2 == open_set[1]:
                        p[open_index].append(open_set[0] + 1)
                        p[open_index].sort()
                        add_new_item(p, open_set[0] + 1)

                if len(single_index) == 1 and len(pair_indices) + len(open_indices) == 0:
                    last_tile = p[single_index[0]][0]
                    p[single_index[0]].append(last_tile)
                    add_new_item(p, last_tile)
        else:
            if was_seven_pairs:
                return finished_hand, win_tile

        return finished_hand, win_tile

    def _pruning_length(len_man, len_pin, len_suo, len_chr):
        lens = [len_man, len_pin, len_suo, len_chr]
        metrics = [l % 3 for l in lens]
        if 1 in metrics:
            if 2 not in metrics and metrics.count(1) == 1:
                return True
        if 2 in metrics:
            if 1 not in metrics and metrics.count(2) == 2:
                return True
        return False
    def _parse_num(nums):
        nums.sort()
        parse_modulos = [WaitCalc._parse_modulo0, WaitCalc._parse_modulo1, WaitCalc._parse_modulo2]
        return parse_modulos[len(nums) % 3](nums, False, False)

    def _parse_chr(hand34):
        if len(hand34) == 1:
            return [[hand34]]
        else:
            melds = [[t]*hand34.count(t) for t in set(hand34)]
            metrics = [len(m) for m in melds]
            if len(hand34) % 3 == 0:
                if metrics.count(3) == len(metrics):
                    return [melds]
            if len(hand34) % 3 == 1:
                if metrics.count(1) == 1 and 2 not in metrics:
                    return [melds]
                if metrics.count(2) == 2 and 1 not in metrics:
                    return [melds]
            if len(hand34) % 3 == 2:
                if metrics.count(2) == 1 and metrics.count(3) + 1 == len(metrics):
                    return [melds]

    @staticmethod
    def _parse_modulo2(nums, has_open, has_single):
        if len(nums) == 2:
            return [[nums]] if abs(nums[0] - nums[1]) < 3 else None
        res = []
        if nums[0] == nums[1] == nums[2]:
            rec_res = WaitCalc._parse_modulo2(nums[3:], has_open, has_single)
            if rec_res:
                for p in rec_res:
                    res.append([nums[0:3]] + p)
        if nums[0] + 2 in nums and nums[0] + 1 in nums:
            rec_tiles = deepcopy(nums)
            rec_tiles.remove(nums[0] + 2)
            rec_tiles.remove(nums[0] + 1)
            rec_tiles.remove(nums[0])
            rec_res = WaitCalc._parse_modulo2(rec_tiles, has_open, has_single)
            if rec_res:
                for p in rec_res:
                    res.append([[nums[0], nums[0] + 1, nums[0] + 2]] + p)
        if nums[0] == nums[1]:
            rec_res = WaitCalc._parse_modulo0(nums[2:], has_open, has_single)
            if rec_res:
                for p in rec_res:
                    res.append([nums[0:2]] + p)
        elif abs(nums[0] - nums[1]) < 3:
            rec_res = WaitCalc._parse_modulo0(nums[2:], True, has_single)
            if rec_res:
                for p in rec_res:
                    res.append([nums[0:2]] + p)
        return res

    @staticmethod
    def _parse_modulo1(nums, has_open, has_single):
        if len(nums) == 1:
            return [[nums]] if not has_single and not has_open else None
        res = []

        if nums[0] == nums[1] == nums[2]:
            rec_res = WaitCalc._parse_modulo1(nums[3:], has_open, has_single)
            if rec_res:
                for p in rec_res:
                    res.append([nums[0:3]] + p)

        if nums[0] + 2 in nums and nums[0] + 1 in nums:
            rec_tiles = deepcopy(nums)
            rec_tiles.remove(nums[0] + 2)
            rec_tiles.remove(nums[0] + 1)
            rec_tiles.remove(nums[0])
            rec_res = WaitCalc._parse_modulo1(rec_tiles, has_open, has_single)
            if rec_res:
                for p in rec_res:
                    res.append([[nums[0], nums[0] + 1, nums[0] + 2]] + p)
        if not has_single:
            if nums[0] == nums[1]:
                rec_res = WaitCalc._parse_modulo2(nums[2:], has_open, has_single)
                if rec_res:
                    for p in rec_res:
                        res.append([nums[0:2]] + p)
            elif abs(nums[0] - nums[1]) < 3:
                rec_res = WaitCalc._parse_modulo2(nums[2:], True, has_single)
                if rec_res:
                    for p in rec_res:
                        res.append([nums[0:2]] + p)

        rec_res = WaitCalc._parse_modulo0(nums[1:], has_open, True)
        if rec_res:
            for p in rec_res:
                res.append([nums[0:1]] + p)
        return res

    @staticmethod
    def _parse_modulo0(nums, has_open, has_single):
        if len(nums) == 3:
            return [[nums]] if nums[0] == nums[1] == nums[2] or nums[0] + 2 == nums[1] + 1 == nums[2] else None
        res = []
        if nums[0] == nums[1] == nums[2]:
            rec_res = WaitCalc._parse_modulo0(nums[3:], has_open, has_single)
            if rec_res:
                for p in rec_res:
                    res.append([nums[0:3]] + p)
        if nums[0] + 2 in nums and nums[0] + 1 in nums:
            rec_tiles = deepcopy(nums)
            rec_tiles.remove(nums[0] + 2)
            rec_tiles.remove(nums[0] + 1)
            rec_tiles.remove(nums[0])
            rec_res = WaitCalc._parse_modulo0(rec_tiles, has_open, has_single)
            if rec_res:
                for p in rec_res:
                    res.append([[nums[0], nums[0] + 1, nums[0] + 2]] + p)
        return res

#print(WaitCalc.waiting_calc([1,1,2,2,4,4,8,8,10,10,21,21,29]))
#print(WaitCalc.waiting_calc([0,1,2,4,6,14,14,14,18,18,23,24,32]))