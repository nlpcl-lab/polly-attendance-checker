import re
import os
import glob
import argparse
import subprocess

from tqdm import tqdm
from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument('--multi', type=int, default=4)
parser.add_argument('--dir', type=str, default='./')

def test_run(pyfile):
    print(pyfile)
    student_no = re.search('[0-9]{8}', pyfile, re.IGNORECASE).group()
    student_path = os.path.join(os.path.dirname(pyfile), student_no)
    os.makedirs(student_path, exist_ok=True)

    stdout = open(os.path.join(student_path, 'stdout.txt'), 'w')
    stderr = open(os.path.join(student_path, 'stderr.txt'), 'w')

    subprocess.call(['python', pyfile], stdout=stdout, stderr=stderr)


def _main(args):
    pool = Pool(processes=args.multi)
    pyfiles = glob.glob(os.path.join(args.dir, '*.py'))
    with tqdm(total=len(pyfiles)) as pbar:
        for _ in tqdm(pool.imap_unordered(test_run, pyfiles)):
            pbar.update()
    pool.close()
    pool.join()
    
    # pool.map(test_run, glob.glob(os.path.join(args.dir, '*.py')))
        

if __name__ == '__main__':
    _main(parser.parse_args())
