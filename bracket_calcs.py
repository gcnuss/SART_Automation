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
    h_pairs - list of tuples, defines pairs of heats grouped together for calculating who
        moves up vs. down for the next round.
    fd_into_ht_pairs - list of tuples, defines pairs of heats grouped together that prior
        heats feed into (i.e. a pair of heats in h_pairs will feed into a pair of heats
        in fd_into_ht_pairs with the first element of the tuple being for the two heat
        winners + next three fastest times, and the second element of the tuple being
        for the remaining 5 times)
    NEXT THREE ARE CURRENTLY HARD CODED FOR: 80 person bracket, 5 people per heat,
        and 2 heat winners + next 3 fastest times as method of advancing; will
        address this flexibility at a future time to add the following parameters:
        bracket_type - int, represents method of progressing people through rounds
        heat_size = int, number of people per heat
        bracket_size = int, total number of people in the bracket

    attributes:
    round - int, round of tournament
    heat - int, heat within given round
    h_seed_key
    '''

    def __init__(self, r0_seeds, h_pairs, fd_into_ht_pairs, columns):
        self.r0_seeds = r0_seeds
        self.h_pairs = h_pairs
        self.fd_into_ht_pairs = fd_into_ht_pairs
        self.columns = columns
        self.h_seed_key = defaultdict(lambda: [], self.r0_seeds)
        self.bef_aft_ht_pairs = zip(sorted(zip(self.h_pairs, self.fd_into_ht_pairs)
        self.sd_h_key = None
        self.bracket_df = None

    def _define_ht_sd_keys(self, pri_heat_pair1, pri_heat_pair2, win_heat, lose_heat):
        self.h_seed_key['Heat {}'.format(win_heat)].append('W{}'.format(pri_heat_pair1))
        self.h_seed_key['Heat {}'.format(win_heat)].append('W{}'.format(pri_heat_pair2))

        for i in range(1,4):
            self.h_seed_key['Heat {}'.format(win_heat)].append('{}/{}-Q{}'.format(
            pri_heat_pair1, pri_heat_pair2, i))

        for i in range(4,9):
            self.h_seed_key['Heat {}'.format(lose_heat)].append('{}/{}-Q{}'.format(
            pri_heat_pair1, pri_heat_pair2, i))

    def _assign_ht_sd_keys(self):

        for pri_heats, wn_ls_heats in self.bef_aft_ht_pairs:
            pri_heat1 = pri_heats[0]
            pri_heat2 = pri_heats[1]
            win_ht = wn_ls_heats[0]
            lose_ht = wn_ls_heats[1]
            self._define_ht_sd_keys(pri_heat1, pri_heat2, win_ht, lose_ht)

    def _assign_flip_sd_ht_keys(self):
        self.sd_h_key = {val:key for key, value in self.h_seed_key.iteritems()
            for i, val in enumerate(value)}

    def prepare_sd_h_keys(self):
        self._assign_ht_sd_keys()
        self._assign_flip_sd_ht_keys()

    def create_bracket(self):
        RH_index = [i for i in self.sd_h_key.keys()]
        self.bracket_df = pd.DataFrame(index=RH_index, columns=self.columns)
        self.bracket_df.index.name = 'Seed'

        for val in self.bracket_df.index:
            self.bracket_df.loc[val,['Nxt_Heat']] = self.sd_h_key[val]
            self.bracket_df.loc[val,['Round']] = int(str(self.bracket_df.loc[
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
    h_pairs = [(101, 102), (103, 104), (105, 106), (107, 108), (109, 110),
    (111, 112), (113, 114), (115, 116), (201, 203), (205, 207), (209, 211),
    (213, 215), (202, 204), (206, 208), (210, 212), (214, 216), (301, 302),
    (303, 304), (305, 306), (307, 308), (309, 310), (311, 312), (313, 314),
    (315, 316), (401, 402), (403, 404), (405, 406), (407, 408), (409, 410),
    (411, 412), (413, 414), (415, 416)]

    #heat pairs round 2 - 5 that prior round feed into e.g. 101, 102 feed into 201, 202:
    fd_into_ht_pairs = [(201, 202), (203, 204), (205, 206), (207, 208),
    (209, 210), (211, 212), (213, 214), (215, 216), (316, 312), (315, 311),
    (314, 310), (313, 309), (308, 304), (307, 303), (306, 302), (305, 301),
    (403, 401), (404, 402), (407, 405), (408, 406), (411, 409), (412, 410),
    (415, 413), (416, 414), (502, 501), (504, 503), (506, 505), (508, 507),
    (510, 509), (512, 511), (514, 513), (516, 515)]

    #Bracket columns:
    columns = ['Round', 'Nxt_Heat', 'First_name', 'Surname', 'Time', 'Nxt_Heat_Time']

    #Heat start times:
    start_times = {'Heat 101': '12:00pm',
             'Heat 102': '12:03pm',
             'Heat 103': '12:06pm',
             'Heat 104': '12:09pm',
             'Heat 105': '12:12pm',
             'Heat 106': '12:15pm',
             'Heat 107': '12:18pm',
             'Heat 108': '12:21pm',
             'Heat 109': '12:24pm',
             'Heat 110': '12:27pm',
             'Heat 111': '12:30pm',
             'Heat 112': '12:33pm',
             'Heat 113': '12:36pm',
             'Heat 114': '12:39pm',
             'Heat 115': '12:42pm',
             'Heat 116': '12:45pm',
             'Heat 201': '3:00pm',
             'Heat 202': '3:03pm',
             'Heat 203': '3:06pm',
             'Heat 204': '3:09pm',
             'Heat 205': '3:12pm',
             'Heat 206': '3:15pm',
             'Heat 207': '3:18pm',
             'Heat 208': '3:21pm',
             'Heat 209': '3:24pm',
             'Heat 210': '3:27pm',
             'Heat 211': '3:30pm',
             'Heat 212': '3:33pm',
             'Heat 213': '3:36pm',
             'Heat 214': '3:39pm',
             'Heat 215': '3:42pm',
             'Heat 216': '3:45pm',
             'Heat 301': '8:00pm',
             'Heat 302': '8:03pm',
             'Heat 303': '8:06pm',
             'Heat 304': '8:09pm',
             'Heat 305': '8:12pm',
             'Heat 306': '8:15pm',
             'Heat 307': '8:18pm',
             'Heat 308': '8:21pm',
             'Heat 309': '8:24pm',
             'Heat 310': '8:27pm',
             'Heat 311': '8:30pm',
             'Heat 312': '8:33pm',
             'Heat 313': '8:36pm',
             'Heat 314': '8:39pm',
             'Heat 315': '8:42pm',
             'Heat 316': '8:45pm',
             'Heat 401': '9:15am',
             'Heat 402': '9:18am',
             'Heat 403': '9:21am',
             'Heat 404': '9:24am',
             'Heat 405': '9:27am',
             'Heat 406': '9:30am',
             'Heat 407': '9:33am',
             'Heat 408': '9:36am',
             'Heat 409': '9:39am',
             'Heat 410': '9:42am',
             'Heat 411': '9:45am',
             'Heat 412': '9:48am',
             'Heat 413': '9:51am',
             'Heat 414': '9:54am',
             'Heat 415': '9:57am',
             'Heat 416': '10:00am',
             'Heat 501': '11:15am',
             'Heat 502': '11:18am',
             'Heat 503': '11:21am',
             'Heat 504': '11:24am',
             'Heat 505': '11:27am',
             'Heat 506': '11:30am',
             'Heat 507': '11:33am',
             'Heat 508': '11:36am',
             'Heat 509': '11:39am',
             'Heat 510': '11:42am',
             'Heat 511': '11:45am',
             'Heat 512': '11:48am',
             'Heat 513': '11:51am',
             'Heat 514': '11:54am',
             'Heat 515': '11:57am',
             'Heat 516': '12:00pm'}
