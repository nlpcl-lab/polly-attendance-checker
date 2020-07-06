import re
import os
import glob
import argparse
import subprocess

from tqdm import tqdm
from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument('--multi', type=int, default=1)
parser.add_argument('--dir', type=str, default='./hw4')

def test_run(folder):
    pyfiles = glob.glob(os.path.join(folder, '*.py'))
    r = re.compile('\.*code_[0-9]{8}')
    mainfile = list(filter(r.search, pyfiles))
    if len(mainfile) == 0:
        print("WARNING! No main file detected")
        return
    if len(mainfile) != 1:
        print("WARNING! More than one main code detected in folder ", folder, mainfile)
        print("filter: ", pyfiles, mainfile)


    mainfind = re.search('CS372.*code_[0-9]{8}.py', mainfile[0])
    if not mainfind:
        print("WARNING! Cannot find a mainfile of format", folder, mainfile)
        return -1
    mainfile = mainfind.group()


    out_log_path = os.path.join(folder, 'stdout.txt')
    err_log_path = os.path.join(folder, 'stderr.txt')

    if os.path.exists(out_log_path) and os.path.exists(err_log_path):
        if os.path.getsize(out_log_path) > 0 and os.path.getsize(err_log_path) == 0: # if it has no error, and has output skip it
            return

    with open(out_log_path, 'w') as stdout, open(err_log_path, 'w') as stderr:
        print("Running... ", folder)
        subprocess.call(['python', mainfile], stdout=stdout, stderr=stderr, cwd=folder)

def get_err_stats(cur_dir):
    errs = list()
    allfiles = os.listdir(cur_dir)
    for fol in allfiles:
        if not os.path.isdir(os.path.join(cur_dir, fol)):  # only use directories
            continue
        foldir = os.path.join(cur_dir, fol)
        errdir = (os.path.join(foldir, 'stderr.txt'))
        if os.path.exists(errdir):
            if os.path.getsize(errdir) > 0:
                errs.append(fol)
    return errs

def folderize_files(args):
    allfiles = os.listdir(args.dir)
    Errors = []
    for file in allfiles: # get all files in the folder
        if os.path.isdir(os.path.join(args.dir,file)): #ignore directories
            continue
        # assuming the format of klms-downloaded file as "Adam Smith_1234321_assignsubmission_file_filename", use the "Adam Smith_1234321" as folder name
        if not re.search('^[^_]*_[^_]*_', file, re.IGNORECASE):
            Errors.append(file) # for files not following this format, add to this list to print later
            continue
        namestr = re.search('^[^_]*_[^_]*_', file, re.IGNORECASE).group(0)[:-1]

        dirname = os.path.join(args.dir, namestr)

        if not os.path.isdir(dirname):
            os.mkdir(dirname)

        # move to directory
        os.rename((os.path.join(args.dir, file)), (os.path.join(dirname, file)))

    if len(Errors) == 0:
        print("No files with unexpected formats. Nice.")
    else:
        print("Found files with unexpected formats")
        print(Errors)

def rename_all_files(args):
    allfiles = os.listdir(args.dir)
    for fol in allfiles:
        if not os.path.isdir(os.path.join(args.dir,fol)): #only use directories
            continue
        foldir =  os.path.join(args.dir, fol)

        for file in os.listdir(foldir):
            match = re.search('^[^_]*_[^_]*_assignsubmission_file_', file, re.IGNORECASE)
            if match:
                head_len = len(match.group(0))
                os.rename((os.path.join(foldir, file)), (os.path.join(foldir, file[head_len:])))


def _main(args):
    folderize_files(args) # put all the files into their folders
    rename_all_files(args) # remove the name headers

    folders = (glob.glob(args.dir+"/*/"))

    with Pool(processes=args.multi) as p:
        with tqdm(total=len(folders)) as pbar:
            for i, _ in enumerate(p.imap_unordered(test_run, folders)):
                pbar.update()

    print('\n' + '-' * 50)
    for err_studentno in get_err_stats(args.dir):
        print(err_studentno)
    
    #pool.map(test_run, glob.glob(os.path.join(args.dir, '*.py')))
        
if __name__ == '__main__':
    _main(parser.parse_args())