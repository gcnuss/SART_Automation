'''Initial definitions, comments on bracket process, format, etc'''

import pandas as pd
import numpy as np
from collections import defaultdict


class SART(object):

    '''Define instance of adventure run tournament class, where a particular
    bracket format (# of rounds, heats per round, feeding calculations, etc),
    number of participants, and start times are defined.  This object can be
    used to run an event, feeding in people's names and times from each round
    to calculate next round placements and progress through the bracket.

    parameters:
    r0_seeds - dict, keys are heats for round 1, values are the round 0 or
        initial seeds that will feed into each round 1 heat.
    h_pairs - dict, defines pairs of heats grouped together for calculating who
        moves up vs. down for the next round.
    fd_into_ht_pairs -
    round - int, round of tournament
    heat - int, heat within given round
    runners - list, names of runners in given heat
        **runners may be a dictionary with times too...need to think about flow
    bracket_type - int, represents method of progressing people through rounds
    heat_size = int, number of people per heat
    bracket_size = int, total number of people in the bracket

    attributes:
    TBD
    '''

    def __init__(self, round, heat, runners, bracket_type):
        self.round = round
        self.heat = heat
        self.runners = runners
        self.bracket_type = bracket_type

    def define_ht_sd_keys(pri_heat_pair1, pri_heat_pair2, win_heat, lose_heat):
        h_seed_key['Heat {}'.format(win_heat)].append('W{}'.format(pri_heat_pair1))
        h_seed_key['Heat {}'.format(win_heat)].append('W{}'.format(pri_heat_pair2))

        for i in range(1,4):
            h_seed_key['Heat {}'.format(win_heat)].append('{}/{}-Q{}'.format(
            pri_heat_pair1, pri_heat_pair2, i))

        for i in range(4,9):
            h_seed_key['Heat {}'.format(lose_heat)].append('{}/{}-Q{}'.format(
            pri_heat_pair1, pri_heat_pair2, i))

    def assign_ht_sd_keys(r0_seeds, bef_aft_ht_pairs):

        h_seed_key = defaultdict(lambda: [], r0_seeds)

        for pri_heats, wn_ls_heats in bef_aft_ht_pairs:
            pri_heat1 = pri_heats[0]
            pri_heat2 = pri_heats[1]
            win_ht = wn_ls_heats[0]
            lose_ht = wn_ls_heats[1]
            define_ht_sd_keys(pri_heat1, pri_heat2, win_ht, lose_ht)

    def assign_flip_sd_ht_keys(h_seed_key):
        sd_h_key = {val:key for key, value in h_seed_key.iteritems()
            for i, val in enumerate(value)}

    def create_bracket(sd_h_key, columns):
        RH_index = [i for i in sd_h_key.keys()]
        bracket_df = pd.DataFrame(index=RH_index, columns=columns)
        bracket_df.index.name = 'Seed'

        for val in bracket_df.index:
            bracket_df.loc[val,['Nxt_Heat']] = sd_h_key[val]
            bracket_df.loc[val,['Round']] = int(str(bracket_df.loc[
                val,['Nxt_Heat']]).split()[2][0])-1

    def process_time_trial_results(raw_csv):
        time_trial_df = pd.read_csv(raw_csv)
        tt_df_cleaned = time_trial_df[['Surname', 'First name', 'Time']]
        tt_df_cleaned = tt_df_cleaned.rename(index=str, columns={'First name': 'First_name'})
        tt_df_cleaned = tt_df_cleaned.sort_values(['Time'])
        tt_df_cleaned['Seed'] = [int(i)+1 for i in tt_df_cleaned.index]

    def assign_next_heat(self, round, heat, runners):
        pass

    def print_round(self, round):
        pass

    def input_times(self, round, heat, times):
        pass

if __name__ == '__main__':
    #2017 SART bracket definitions to instantiate class instance:

    #round 0 heat / seed groupings:
    r0_seeds = {'Heat 101': [1, 32, 33, 64, 65], 'Heat 102': [16, 17, 48, 49, 80],
    'Heat 103': [8, 25, 40, 57, 72], 'Heat 104': [9, 24, 41, 56, 73],
    'Heat 105': [4, 29, 36, 61, 68], 'Heat 106': [13, 20, 45, 52, 77],
    'Heat 107': [5, 28, 37, 60, 69], 'Heat 108': [12, 21, 44, 53, 76],
    'Heat 109': [2, 31, 34, 63, 66], 'Heat 110': [15, 18, 47, 50, 79],
    'Heat 111': [7, 26, 39, 58, 71], 'Heat 112': [10, 23, 42, 55, 74],
    'Heat 113': [3, 30, 35, 62, 67], 'Heat 114': [14, 19, 46, 51, 78],
    'Heat 115': [6, 27, 38, 59, 70], 'Heat 116': [11, 22, 43, 54, 75]}

    #heat pairs round 1 - 4:
    h_pairs = {101: 102, 103: 104, 105: 106, 107: 108, 109: 110, 111:112, 113: 114, 115: 116,
    201: 203, 205: 207, 209: 211, 213: 215, 202: 204, 206: 208, 210: 212, 214: 216,
    301: 302, 303: 304, 305: 306, 307: 308, 309: 310, 311: 312, 313: 314, 315: 316,
    401: 402, 403: 404, 405: 406, 407: 408, 409: 410, 411: 412, 413: 414, 415: 416}

    #heat pairs round 2 - 5 that prior round feed into e.g. 101, 102 feed into 201, 202:
    fd_into_ht_pairs = [(201, 202), (203, 204), (205, 206), (207, 208), (209, 210), (211, 212),
    (213, 214), (215, 216), (316, 312), (315, 311), (314, 310), (313, 309),
    (308, 304), (307, 303), (306, 302), (305, 301), (403, 401), (404, 402),
    (407, 405), (408, 406), (411, 409), (412, 410), (415, 413), (416, 414),
    (502, 501), (504, 503), (506, 505), (508, 507), (510, 509), (512, 511),
    (514, 513), (516, 515)]

    #combined heat data for full bracket flow through:
    bef_aft_ht_pairs = zip(sorted(zip(h_pairs.keys(), h_pairs.values())), fd_into_ht_pairs)

    #Bracket columns:
    columns = ['Round', 'Nxt_Heat', 'First_name', 'Surname', 'Time']
