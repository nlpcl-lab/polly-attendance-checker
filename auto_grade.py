import os
import csv
import glob
import argparse

parser.add_argument('--dir', type=str, default='./')

def get_stats(cur_dir):
    stats = list()
    for student_dir in glob.glob(os.path.join(cur_dir, '*/')):
        if os.path.getsize(os.path.join(student_dir, 'stderr.txt')) > 0:
            with open(os.path.join(student_dir, 'stderr.txt'), 'r') as f:
                stats.append([student_dir.split('/')[-2],
                              'X: %s' % f.read().replace('\n', ' ')])
        else:
            stats.append([student_dir.split('/')[-2], 'O'])
        

def _main():
    stats = get_stats(args.dir)
    with open('student_stats.csv', 'w', encoding='utf-8') as f:
        wr = csv.writer(f)
        for stat in stats:
            wr.writerow(stat)

if __name__ == '__main__':
    _main(parser.parse_args())