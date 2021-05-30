# external drives must be mounted beforehand
import os
import sys
import eyed3
import shutil
from pathlib import Path
from io import StringIO


USERDIR = '/media/daniel/volume-exFa/Musica/Unsorted/complete/'
SORTEDDIR = '/media/daniel/volume-exFa/Musica/Sorted/'
KEEP = True

class clrs:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Not used (yet). grabs eyed3 stdout for eyed3.load
class capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio
        sys.stdout = self._stdout

def flatten_list(var):
     flat_list = [item for sublist in var for item in sublist]
     return flat_list

full_paths = []
path_nfo = {}
for root, dirs, files in os.walk(USERDIR, topdown=True):
    path_nfo['root'] = root
    path_nfo['dirs'] = dirs
    path_nfo['files'] = files
    for name in files:
        full_paths.append(os.path.join(root, name))

path_dct = {}
for file in full_paths:
    ext = os.path.splitext(file)[1]
    if ext and ext == '.mp3':
        with capturing() as output:
            audiofile = eyed3.load(file)
        if audiofile.tag.artist is not None:
            artist = audiofile.tag.artist
            print('Artist - ' + artist)
            if not os.path.exists(SORTEDDIR + artist):
                os.makedirs(SORTEDDIR + artist)
        else:
            print('\nWARNING - Artist tag not found\n')
            continue
        if audiofile.tag.album is not None:
            album = audiofile.tag.album
            print('Album - ' + album + '\n')
            new_dir = Path(SORTEDDIR + artist + '/' + album + '/')
            new_fpath = new_dir / os.path.basename(file)
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            shutil.copyfile(file, new_fpath)
            path_dct[(artist, album)] = [Path(file).parent, new_dir]
        else:
            print('\nWARNING - Album tag not found\n.')
            continue

if KEEP:
    for file in full_paths:
        ext = os.path.splitext(file)[1]
        if not ext or ext != '.mp3':
            misc_dir = Path(file).parent
            for dir in path_dct.values():
                if misc_dir == dir[0]:
                    new_fpath = dir[1] / os.path.basename(file)
                    shutil.copyfile(file, new_fpath)
                    print('\nCopied ', os.path.basename(file),
                        'to ', new_fpath)

