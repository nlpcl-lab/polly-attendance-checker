import argparse
import glob
import os
import re
import subprocess
import zipfile
from multiprocessing import Pool

from tqdm import tqdm

from gap_scorer import run_scorer


def _main(args):
    unzip_all_to_data(args)
    print('Done. Now see %s folder for more details.' % args.output_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--gold_tsv', type=str, required=True)
    parser.add_argument('--multi', type=int, default=8)
    parser.add_argument('--input_dir', type=str, required=True,
                        help='The directory where all submission zip files are included')
    parser.add_argument('--output_dir', type=str, default='./data/')
    _main(parser.parse_args())
