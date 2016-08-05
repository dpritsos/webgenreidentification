#!/usr/bin/env python

import sys
sys.path.append('../../teca')
sys.path.append('../../../DoGSWrapper/dogswrapper')

import tables as tb
import numpy as np
import collections as coll
from data_retrieval.data import multiclass_res
from data_retrieval.data import rfse_multiclass_multimeasure_res
from data_retrieval.data import rfse_onevsall_res
from data_retrieval.data import rfse_onevsall_multimeasure_res
import base.param_combs as param_comb
import analytics.metrix as mx


def PRConf_table(h5d_fl1, h5d_fl2, kfolds, params_path, mix, strata, unknown_class, prereccon=0):
    """Precision Recall Tables and Contigency tables from H5D files.

        ### Make proper Definition here ###

    """

    # Beginning Contingency table building
    if mix:
        rfse_data = rfse_multiclass_multimeasure_res(
            h5d_fl1, h5d_fl2, kfolds, params_path, binary=False, strata=strata
        )

    else:
        rfse_data = multiclass_res(
            h5d_fl1, kfolds, params_path, binary=False, strata=strata
        )

    # 3rd element contain predicted y values list.
    pred_y = rfse_data[2]

    # 2rd element contain predicted y values list.
    exp_y = rfse_data[1]

    # Calculating contigency table.
    conf_mtrx = mx.contingency_table(exp_y, pred_y, unknown_class=unknown_class, arr_type=np.int32)

    if prereccon in [0, 1]:
        # Calculating precision recall scores.
        pr_tbl = mx.precision_recall_scores(conf_mtrx)

    if prereccon in [0, 2]:
        col_sums = conf_mtrx.sum(axis=0)
        conf_mtrx = np.vstack((conf_mtrx, col_sums))
        # conf_percent = np.divide(conf_mtrx, np.bincount(expected_y)) * 100

    if prereccon == 0:
        # Returning...
        return (pr_tbl, conf_mtrx)
    elif prereccon == 1:
        # Returning...
        return pr_tbl
    elif prereccon == 2:
        # Returning...
        return conf_mtrx
    else:
        raise Exception("Returning mode 'prereccon' variable invalid value. Valid values {0,1,2}.")


# One Run for all cases
if __name__ == '__main__':

    # Parameters used for the experiments required for selecting specific or group of results
    kfolds = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # case_od = coll.OrderedDict([
    #    ('doc_rep', ['3Words', '1Words', '4Chars']),
    #    ('corpus', ['7Genres', 'KI04', 'SANTINIS']),
    #    ('dist', ['', 'MinMax', 'MIX']),  #, 'MinMax', 'MIX'
    #    ('vocab_size', [5000, 10000, 50000, 100000]),
    #    ('features_size', [1000, 5000, 10000, 50000, 90000]),
    #    #('nu', [0.05, 0.07, 0.1, 0.15, 0.17, 0.3, 0.5, 0.7, 0.9])
    #    ('Sigma', [0.5, 0.7, 0.9]),
    #    ('Iterations', [10, 50, 100])
    # ])

    case_od = coll.OrderedDict([
        ('doc_rep', ['4Chars', ]),
        ('corpus', ['7Genres', ]),
        ('dist', ['', ]),
        ('vocab_size', [100000]),
        ('features_size', [90000]),
        ('nu', [0.1, ])
        # ('Sigma', [0.5, 0.7, 0.9]),
        # ('Iterations', [10, 50, 100])
    ])

    # Creating tables for tall the above cases.
    for case, case_path in zip(
        param_comb.ParamGridIter(case_od, 'list'),
            param_comb.ParamGridIter(case_od, 'path')):

        if case[3] > case[4]:

            print case

            # Selecting filepath
            if case[1] == '7Genres':
                h5d_fl = '/home/dimitrios/Synergy-Crawler/Santinis_7-web_genre/OCSVM_'

            elif case[1] == 'KI04':
                h5d_fl = '/home/dimitrios/Synergy-Crawler/KI-04/OCSVM_'

            else:
                h5d_fl = '/home/dimitrios/Synergy-Crawler/SANTINIS/OCSVM_'

            h5d_fl = h5d_fl + case[0] + '_' + case[1]

            # Selecting files to open and setting the mix flag on/off
            mix = False

            if case[2] == 'MIX':
                h5d_fl1 = tb.open_file(h5d_fl + '.h5', 'r')
                h5d_fl2 = tb.open_file(h5d_fl + '_minmax.h5', 'r')
                mix = True

            elif case[2] == 'MinMax':
                h5d_fl1 = tb.open_file(h5d_fl + '_minmax.h5', 'r')
                h5d_fl2 = h5d_fl1

            else:
                h5d_fl1 = tb.open_file(h5d_fl + '.h5', 'r')
                h5d_fl2 = h5d_fl1

            # Defining save file name
            conf_mtrx_fname = '/home/dimitrios/Documents/MyPublications:Journals-Conferences/' + \
                'Journal_IPM-Elsevier/tables_data/Confusion_tables/Conf_'

            pr_tabel_fname = '/home/dimitrios/Documents/MyPublications:Journals-Conferences/' + \
                'Journal_IPM-Elsevier/tables_data/PR_tables/PRTbl_'

            conf_mtrx_fname = conf_mtrx_fname + '_'.join(case[0:3]) + \
                '_pset(' + ','.join([str(i) for i in case[3::]]) + ')'
            conf_mtrx_fname = conf_mtrx_fname.replace('__', '_Cos_')  # _Cos_ OCSVME
            conf_mtrx_fname = conf_mtrx_fname.replace('0.', '0')
            conf_mtrx_fname = conf_mtrx_fname + '.csv'

            pr_tabel_fname = pr_tabel_fname + '_'.join(case[0:3]) + \
                '_pset(' + ','.join([str(i) for i in case[3::]]) + ')'
            pr_tabel_fname = pr_tabel_fname.replace('__', '_Cos_')   # _Cos_
            pr_tabel_fname = pr_tabel_fname.replace('0.', '0')
            pr_tabel_fname = pr_tabel_fname + '.csv'

            # Reformationg parametera path to be given properly to the h5d_pre_rec_table function.
            params_path = '/' + '/'.join(case_path.split('/')[4::])
            # print pr_tabel_fname

            # Calculating the tables
            pr_tabel, conf_mtrx = PRConf_table(
                h5d_fl1, h5d_fl2, kfolds, params_path, case[5], mix, strata=None,
                unknown_class=True, prereccon=0
            )

            # Saving tables
            # np.savetxt(conf_mtrx_fname, conf_mtrx)

            # pr_tabel[np.where((pr_tabel==np.NaN))] = 0.0
            # np.savetxt(pr_tabel_fname, pr_tabel)

            np.set_printoptions(precision=3, threshold=10000, suppress=True, linewidth=100)
            print pr_tabel
            # print conf_mtrx
            # print pr_scores[:, :]"""

            # Closing HDF5 files
            if case[2] == 'MIX':
                h5d_fl1.close()
                h5d_fl2.close()
            else:
                h5d_fl1.close()
