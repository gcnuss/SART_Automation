from __future__ import print_function
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

    def __init__(self, r0_seeds, h_pairs, fd_into_ht_pairs, columns, start_times):
        self.r0_seeds = r0_seeds
        self.h_pairs = h_pairs
        self.fd_into_ht_pairs = fd_into_ht_pairs
        self.columns = columns
        self.start_times = start_times
        self.h_seed_key = defaultdict(lambda: [], self.r0_seeds)
        self.bef_aft_ht_pairs = zip(self.h_pairs, self.fd_into_ht_pairs)
        self.sd_h_key = None
        self.bracket_df = None
        self.tt_df_cleaned = None

    def _define_ht_sd_keys(self, pri_heat_pair1, pri_heat_pair2, win_heat, lose_heat):
        self.h_seed_key['Heat {}'.format(win_heat)].append('W{}'.format(pri_heat_pair1))
        self.h_seed_key['Heat {}'.format(win_heat)].append('W{}'.format(pri_heat_pair2))

        for i in range(1,4):
            self.h_seed_key['Heat {}'.format(win_heat)].append('{}/{}-Q{}'.format(pri_heat_pair1, pri_heat_pair2, i))

        for i in range(4,9):
            self.h_seed_key['Heat {}'.format(lose_heat)].append('{}/{}-Q{}'.format(pri_heat_pair1, pri_heat_pair2, i))

    def _assign_ht_sd_keys(self):
        for pri_heats, wn_ls_heats in self.bef_aft_ht_pairs:
            pri_heat1 = pri_heats[0]
            pri_heat2 = pri_heats[1]
            win_ht = wn_ls_heats[0]
            lose_ht = wn_ls_heats[1]
            self._define_ht_sd_keys(pri_heat1, pri_heat2, win_ht, lose_ht)

    def _assign_flip_sd_ht_keys(self):
        self.sd_h_key = {val:key for key, value in self.h_seed_key.iteritems() for i, val in enumerate(value)}

    def prepare_sd_h_keys(self):
        self._assign_ht_sd_keys()
        self._assign_flip_sd_ht_keys()

    def create_bracket(self):
        RH_index = [i for i in self.sd_h_key.keys()]
        self.bracket_df = pd.DataFrame(index=RH_index, columns=self.columns)
        self.bracket_df.index.name = 'Seed'

        for val in self.bracket_df.index:
            self.bracket_df.loc[val,['Nxt_Heat']] = self.sd_h_key[val]
            self.bracket_df.loc[val,['Round']] = int(str(self.bracket_df.loc[val,['Nxt_Heat']]).split()[2][0])-1

        for key, time in self.start_times.iteritems():
            self.bracket_df['Nxt_Heat_Time'][self.bracket_df['Nxt_Heat'] == key] = time

        self.bracket_df.sort_index(inplace=True)

    def process_time_trial_results(self, raw_csv):
        time_trial_df = pd.read_csv(raw_csv)
        self.tt_df_cleaned = time_trial_df[['Surname', 'First name', 'Time']]
        self.tt_df_cleaned = self.tt_df_cleaned.rename(index=str, columns={'First name': 'First_name'})
        self.tt_df_cleaned = self.tt_df_cleaned.sort_values(['Time'])
        self.tt_df_cleaned['Seed'] = [int(i)+1 for i in self.tt_df_cleaned.index]

    def _check_TT_for_ties(self):
        unique_len = len(set(self.tt_df_cleaned['Time']))
        original_len = len(self.tt_df_cleaned)

        if unique_len != original_len:
            return 'Warning: Ties exist - diff in list length is {}.  Fix before proceeding.'.format((original_len - unique_len))
        else:
            return 'No Ties, results added to bracket!'

    def add_time_trial_results(self):
        tie_status = self._check_TT_for_ties()
        print (tie_status)

        if tie_status != 'No Ties, results added to bracket!':
            return

        for val in self.tt_df_cleaned['Seed']:
            self.bracket_df.loc[val,['First_name']] = (self.tt_df_cleaned['First_name'][self.tt_df_cleaned['Seed'] == val].item())
            self.bracket_df.loc[val,['Surname']] = (self.tt_df_cleaned['Surname'][self.tt_df_cleaned['Seed'] == val].item())
            self.bracket_df.loc[val,['Time']] = (self.tt_df_cleaned['Time'][self.tt_df_cleaned['Seed'] == val].item())

    def clean_results_csv(self, raw_csv):
        df = pd.read_csv(raw_csv)
        df = df[['Surname', 'First name', 'Time', 'Entry cl. No']]
        df = df.rename(index=str, columns={'First name': 'First_name'})
        df = df.rename(index=str, columns={'Entry cl. No': 'Heat'})
        df = df.sort_values(['Time'])
        return df

    def _check_heats_for_ties(self, temp_df1, temp_df2, ht1, ht2):
        temp_df = pd.concat([temp_df1, temp_df2])
        unique_len = len(set(temp_df['Time']))
        original_len = len(temp_df)

        if unique_len != original_len:
            return 'Warning: Ties exist in Heat Pair {},{}.  Must fix before proceeding.'.format(ht1, ht2)
        else:
            return 'No Ties, proceeding with next heat assignments!'

    def nxt_ht_assigns(self, results_df, rnd, person_info=['Surname', 'First_name', 'Time']):
        '''define inputs, how function works'''
        for ht1, ht2 in self.h_pairs:
            if ht1 < (rnd * 100 + 100) and ht1 > ((rnd - 1) * 100 + 100):
                temp_df1 = results_df[(results_df['Heat'] == ht1)].sort_values('Time')
                temp_df1.reset_index(drop=True, inplace=True)
                temp_df2 = results_df[(results_df['Heat'] == ht2)].sort_values('Time')
                temp_df2.reset_index(drop=True, inplace=True)

                tie_status = self._check_heats_for_ties(temp_df1, temp_df2, ht1, ht2)
                print (tie_status)

                if tie_status != 'No Ties, proceeding with next heat assignments!':
                    break

                for colnm in person_info:
                    ht_win1 = temp_df1[colnm][temp_df1['Time'] == temp_df1['Time'].min()].item()
                    self.bracket_df.loc['W{}'.format(ht1),[colnm]] = ht_win1
                    ht_win2 = temp_df2[colnm][temp_df2['Time'] == temp_df2['Time'].min()].item()
                    self.bracket_df.loc['W{}'.format(ht2),[colnm]] = ht_win2

                temp_df1.drop(0, inplace=True)
                temp_df2.drop(0, inplace=True)
                temp_dftot = pd.concat([temp_df1, temp_df2]).sort_values('Time')
                temp_dftot.reset_index(drop=True, inplace=True)

                for i, row in enumerate(temp_dftot.values):
                    for j, colnm in enumerate(person_info):
                        self.bracket_df.loc['{}/{}-Q{}'.format(ht1, ht2, i+1),[colnm]] = row[j]

    def print_heat_assigns(self, rnd):
        info_list = []

        for heat in xrange((rnd*100 + 1), (rnd*100 + 17)):
            df = self.bracket_df[self.bracket_df['Nxt_Heat'] == 'Heat {}'.format(heat)].sort_values('Time')
            info_list.append('Heat {}'.format(heat))
            info_list.append('\n')
            info_list.append(df[['First_name', 'Surname', 'Nxt_Heat_Time']])
            info_list.append('\n')

        return info_list

    def assign_nxt_ht_to_ss_import_csv(self, csv_imp_file, prior_rnd):
        ss_input = pd.read_csv(csv_imp_file)
        ss_input = ss_input[pd.notnull(ss_input['Surname'])]
        bracket_df_temp = self.bracket_df[(pd.notnull(self.bracket_df['Surname'])) & (self.bracket_df['Round'] == prior_rnd)]

        if len(ss_input) != len(bracket_df_temp):
            return 'Warning: mismatch between next round import file and current round results lists - check data! ss_input length is {} and bracket_df_temp length is {}'.format(len(ss_input), len(bracket_df_temp))
        else:
            for val in ss_input.index:
                ss_input.loc[val, ['Long']] = bracket_df_temp[
                    (bracket_df_temp['Round'] == prior_rnd) &
                    (bracket_df_temp['Surname'] == ss_input.loc[
                    val, ['Surname']].values[0]) & (bracket_df_temp[
                    'First_name'] == ss_input.loc[
                    val, ['First name']].values[0])]['Nxt_Heat'].values[0]

                ss_input.loc[val, ['Short']] = 'H' + ss_input.loc[val, ['Long']].values[0][-3:]
                ss_input.loc[val, ['Cl. no.']] = ss_input.loc[val, ['Long']].values[0][-3:]

            return ss_input

    def _check_finals_for_ties(self, r5_results):

        for heat in xrange(501, 517):
            if len(set(r5_results[r5_results['Heat']==heat]['Time'])) == len(r5_results[r5_results['Heat']==heat]):
                return 'No ties, proceeding with print out'
            else:
                return 'Ties exist in Heat {}.  Fix before proceeding!'.format(heat)

    def print_final_results(self, r5_results):
        info_list = []

        tie_status = self._check_finals_for_ties(r5_results)
        print (tie_status)

        if tie_status == 'No ties, proceeding with print out':
            pass
        else:
            return

        for heat in xrange(516, 500, -1):
            df = r5_results[r5_results['Heat'] == heat]
            info_list.append('Heat {}'.format(heat))
            info_list.append('\n')
            info_list.append(df[['First_name', 'Surname', 'Time']])
            info_list.append('\n')

        return info_list
