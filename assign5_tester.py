import argparse
import glob
import os
import pickle
import re
import shutil
import subprocess
import zipfile
from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm

from gap_scorer import Gender, Scores, calculate_scores, read_annotations

GENDER = ['Overall', 'Masculine', 'Feminine']
COLUMNS = ['snippet(%s)' % x for x in GENDER] + \
          ['page(%s)' % x for x in GENDER] + \
          ['is_duplicated_snippet', 'is_duplicated_page']
DISPLAY_NAMES = [(None, 'Overall'), (Gender.MASCULINE, 'Masculine'),
                 (Gender.FEMININE, 'Feminine')]


def clear_data(args):
    all_dirs_and_files = glob.glob(os.path.join(args.output_dir, '**'))

    with Pool(processes=args.multi) as p:
        with tqdm(total=len(all_dirs_and_files)) as pbar:
            for _ in enumerate(p.imap_unordered(shutil.rmtree, all_dirs_and_files)):
                pbar.update()


def unzip(item):
    student_path, filename = item
    if not os.path.isdir(student_path):
        os.mkdir(student_path)

    try:
        submission_zipfile = zipfile.ZipFile(filename)
        submission_zipfile.extractall(path=student_path)
        return (True, None)
    except:
        return (False, filename)


def unzip_all_to_data(args):
    zipfiles = glob.glob(os.path.join(args.input_dir, '*.zip')) + \
        glob.glob(os.path.join(args.input_dir, '*.rar'))

    student_names = list()
    student_paths = list()
    for filename in zipfiles:
        student_name = re.search(
            '([A-z]| |-|_)+(?=_[0-9]{7}_)', filename, re.IGNORECASE).group(0)
        student_names.append(student_name)

        student_path = os.path.join(args.output_dir, student_name)
        student_paths.append((student_path, filename))

    errfile = open('err.log', 'w')

    with Pool(processes=args.multi) as p:
        with tqdm(total=len(student_paths)) as pbar:
            for _, item in enumerate(p.imap_unordered(unzip, student_paths)):
                pbar.update()
                if not item[0]:
                    errfile.write('%s\n' % item[1])
    errfile.close()
    return student_names


def get_gender_scores(scores):
    return {display_name: scores.get(gender, Scores()).f1() for gender, display_name in DISPLAY_NAMES}


def update_summaries(gold, system_tsv, name, summaries, student_name):
    if system_tsv is None:
        for gender in GENDER:
            summaries.loc[student_name, name % gender] = -1
        return

    system_annotations = read_annotations(system_tsv, is_gold=False)
    system_scores = calculate_scores(gold, system_annotations)
    del system_annotations

    gender_scores = get_gender_scores(system_scores)
    for gender in gender_scores.keys():
        summaries.loc[student_name, name % gender] = gender_scores[gender]

    # MERCY CODE #
    # if sum(gender_scores.values()) == 0:
    #     system_annotations = read_annotations(system_tsv, is_gold=True)
    #     system_scores = calculate_scores(gold, system_annotations)
    #     del system_annotations

    #     gender_scores = get_gender_scores(system_scores)
    #     for gender in gender_scores.keys():
    #         summaries.loc[student_name, name % gender] = gender_scores[gender]
    # END OF MERCY CODE #


def get_snippet_and_page_tsvs(args, student_name):
    tsvs = glob.glob(os.path.join(
        args.output_dir, str(student_name), '*.tsv'))
    snippet_tsv, page_tsv = None, None
    for tsv in tsvs:
        if tsv.find('snippet') >= 0:
            snippet_tsv = tsv
        if tsv.find('page') >= 0:
            page_tsv = tsv

    return snippet_tsv, page_tsv


def check_scores(args, summaries, names):
    gold_annotations = read_annotations(args.gold_tsv, is_gold=True)

    for student_name in tqdm(names):
        snippet_tsv, page_tsv = get_snippet_and_page_tsvs(args, student_name)

        update_summaries(gold_annotations, snippet_tsv, 'snippet(%s)',
                         summaries, student_name)
        update_summaries(gold_annotations, page_tsv,
                         'page(%s)', summaries, student_name)


def check_duplicates(args, summaries, names):
    dfs = dict()

    for student_name in tqdm(names):
        snippet_tsv, page_tsv = get_snippet_and_page_tsvs(args, student_name)

        dfs[student_name] = (read_annotations(snippet_tsv, is_gold=False) if snippet_tsv else None,
                             read_annotations(page_tsv, is_gold=False) if page_tsv else None)

    for student_name in tqdm(dfs.keys()):
        if dfs[student_name][0] == None:
            continue

        for another_student_name in tqdm(dfs.keys()):
            if student_name == another_student_name:
                continue
            if dfs[another_student_name][0] == None:
                continue
            if dfs[student_name][0] == dfs[another_student_name][0]:
                summaries.loc[student_name,
                              'is_duplicated_snippet'] = another_student_name
        else:
            summaries.loc[student_name, 'is_duplicated_snippet'] = 0

        if dfs[student_name][1] == None:
            continue

        for another_student_name in tqdm(dfs.keys()):
            if student_name == another_student_name:
                continue
            if dfs[another_student_name][1] == None:
                continue
            if dfs[student_name][1] == dfs[another_student_name][1]:
                summaries.loc[student_name,
                              'is_duplicated_page'] = another_student_name
        else:
            summaries.loc[student_name, 'is_duplicated_page'] = 0


def check_run(args):
    NotImplemented


def _main(args):
    if args.clear:
        print('===DATA CLEANING===')
        clear_data(args)
        print('')

    print('===DATA UNZIP===')
    student_names = None
    if args.cache:
        with open('student_names.pkl', 'rb') as f:
            student_names = pickle.load(f)
    else:
        student_names = unzip_all_to_data(args)
        with open('student_names.pkl', 'wb') as f:
            pickle.dump(student_names, f)
    student_summaries = pd.DataFrame(
        columns=COLUMNS)
    # student_summaries.set_index('student_name')

    print('\n===SCORE CHECK===')
    check_scores(args, student_summaries, student_names)

    print('\n===DUPLICATE CHECK===')
    check_duplicates(args, student_summaries, student_names)

    # check_run(args)

    student_summaries.to_csv(args.output_file, sep='\t')
    print('\nDone. Now see %s for more details.' % args.output_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gold_tsv', type=str, required=True)
    parser.add_argument('--multi', type=int, default=8)
    parser.add_argument('--input_dir', type=str, required=True,
                        help='The directory where all submission zip files are included')
    parser.add_argument('--output_dir', type=str, default='./data/')
    parser.add_argument('--clear', action='store_true')
    parser.add_argument('--output_file', type=str, default='./summary.tsv')
    parser.add_argument('--cache', action='store_true')
    _main(parser.parse_args())
