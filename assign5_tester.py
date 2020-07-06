import argparse
import glob
import os
import re
import subprocess
import zipfile
from multiprocessing import Pool

import pandas as pd
from tqdm import tqdm

from gap_scorer import calculate_scores

GENDER = ['Overall', 'Masculine', 'Feminine']
COLUMNS = ['student_no'] + \
          ['snippet(%s)' % x for x in GENDER] + \
          ['page(%s)' % x for x in GENDER] + \
          ['is_duplicated_snippet', 'is_duplicated_page']


def clear_data(output_dir):
    all_dirs_and_files = glob.glob(os.path.join(output_dir, '**'))
    all_dirs_and_files.remove(os.path.join(output_dir, '.gitkeep'))
    for dir_or_file in all_dirs_and_files:
        os.remove(dir_or_file)


def unzip_all_to_data(args):
    zipfiles = glob.glob(os.path.join(args.input_dir, '*.zip')) + \
        glob.glob(os.path.join(args.input_dir, '*.rar'))

    student_numbers = list()

    for filename in zipfiles:
        student_number = re.search(
            '[0-9]{8}', filename, re.IGNORECASE).group(0)
        student_path = os.path.join(args.output_dir, 'student_number')

        student_numbers.append(int(student_number))

        if not os.path.isdir(student_path):
            os.mkdir(student_path)
        submission_zipfile = zipfile.ZipFile()
        submission_zipfile.extractall(path=student_path)

    return student_numbers


def check_scores(args, summaries):
    for student_no in student_summaries['student_no']:
        tsvs = glob.glob(os.path.join(
            args.output_dir, str(student_no), '*.tsv'))
        snippet_tsv = tsvs[0] if tsv[0].find('snippet') >= 0 else tsvs[1]
        page_tsv = tsvs[1] if tsv[1].find('page') >= 0 else tsvs[0]


def check_duplicates(args, summaries):
    NotImplemented


def check_run(args):
    NotImplemented


def _main(args):
    if args.clear:
        clear_data(args.output_dir)
    student_numbers = unzip_all_to_data(args)
    student_summaries = pd.DataFrame(
        columns=COLUMNS)
    student_summaries.set_index('student_no')
    student_summaries['student_no'] = student_numbers
    check_scores(args, student_summaries)
    check_duplicates(args, student_summaries)
    # check_run(args)
    print('Done. Now see %s folder for more details.' % args.output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gold_tsv', type=str, required=True)
    parser.add_argument('--multi', type=int, default=8)
    parser.add_argument('--input_dir', type=str, required=True,
                        help='The directory where all submission zip files are included')
    parser.add_argument('--output_dir', type=str, default='./data/')
    parser.add_argument('--clear', action='store_true')
    _main(parser.parse_args())
