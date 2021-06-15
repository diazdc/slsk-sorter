# external drives must be mounted beforehand
import os
import sys
import eyed3
import shutil
from pathlib import Path
from io import StringIO

"""
if using wsl2:
sudo mount -t drvfs E: /home/diazdc/external-volume/
make sure you copy absolute paths from vscode sidebar
"""

USERDIR = '/home/diazdc/external-volume/Musica/Unsorted/complete/'
SORTEDDIR = '/home/diazdc/external-volume/Musica/Sorted/'
KEEP = True

class clrs:
    RED = '\033[31m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

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

if not os.path.exists(USERDIR):
    print(f'{clrs.RED}ERROR{clrs.ENDC}: User download directory doesn\'t exist')

if not os.path.exists(SORTEDDIR):
    print(f'{clrs.RED}ERROR{clrs.ENDC}: User sorted directory doesn\'t exist')

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
        print_song = f'Song - {clrs.RED}{os.path.basename(file)}{clrs.ENDC}'
        with capturing() as output:
            audiofile = eyed3.load(file)
        if audiofile.tag.artist is not None:
            artist = audiofile.tag.artist
            print_artist = 'Artist - ' + f'{clrs.RED}{artist}{clrs.ENDC}'
            if not os.path.exists(SORTEDDIR + artist):
                os.makedirs(SORTEDDIR + artist)
        else:
            print('\n{clrs.WARNING}WARNING: Artist tag not found{clrs.ENDC}\n')
            continue
        if audiofile.tag.album is not None:
            album = audiofile.tag.album
            print_album = 'Album - ' + f'{clrs.RED}{album}{clrs.ENDC}' + '\n'
            new_dir = Path(SORTEDDIR + artist + '/' + album + '/')
            new_fpath = new_dir / os.path.basename(file)
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            if os.path.exists(new_fpath):
                print(f'{clrs.WARNING}Skipping{clrs.ENDC}, file exists \n',
                    f'{print_song}\n')
            else:
                print(f'{clrs.CYAN}Copying{clrs.ENDC}\n',
                 f'{print_artist}\n {print_album} {print_song}\n')
                shutil.copyfile(file, new_fpath)
            path_dct[(artist, album)] = [Path(file).parent, new_dir]
        else:
            print(f'\n{clrs.WARNING}WARNING: Album tag not found{clrs.ENDC}\n')
            continue

if KEEP:
    for file in full_paths:
        ext = os.path.splitext(file)[1]
        if not ext or ext != '.mp3':
            misc_dir = Path(file).parent
            for dir in path_dct.values():
                if misc_dir == dir[0]:
                    to_copy = os.path.basename(file)
                    new_fpath = dir[1] / to_copy
                    shutil.copyfile(file, new_fpath)
                    print('\nCopied', f'{clrs.RED}{to_copy}{clrs.ENDC}',
                        'to', new_fpath)

