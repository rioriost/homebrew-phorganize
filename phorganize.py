#!/usr/bin/env python3

import sys
import os
import shutil
import argparse
import subprocess
from datetime import datetime, timezone, timedelta
import glob
import xml

# python-magic
try:
    import magic
except ModuleNotFoundError:
    sys.exit("Please install python-magic, 'pip3 install python-magic'\n")
except ImportError:
    sys.exit("Please install libmagic, 'brew install libmagic'\n")

# definition of targeted mime types
# This list means what mime types I tested with
targeted_mime_types = {}
targeted_mime_types['image'] = [
    "image/jpeg",
    "image/heic",
    "image/png",
    "image/tiff",
    "image/x-canon-crw",
    "image/x-canon-cr2",
    "image/x-fuji-raf",
    "image/x-x3f",
    "image/x-olympus-orf",
    ]
targeted_mime_types['video'] = [
    "video/mp4",
    "video/quicktime",
    "application/octet-stream",
    ]

# definition of command arguments
def set_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description = "Organize the photos and the videos using embedded meta data in the files")
    parser.add_argument("input",
        help = "Input path of photos and videos or directory to find them")
    parser.add_argument("--verbose", "-v",
        help = "increase output (V)erbosity",
        action = "store_true")
    parser.add_argument("--move", "-m",
        help = "(M)ove files to sub-directories, not copy",
        action = "store_true")
    parser.add_argument("--rename", "-r",
        help = "(R)ename files, NOT maintain original name",
        action = "store_true")
    parser.add_argument("--recursive",
        help = "Find files recursively within input directory",
        default = False,
        action = "store_true")
    parser.add_argument("--camera", "-c",
        help = "make sub-directories with (C)amera model",
        action = "store_true")
    parser.add_argument("--output", "-o", 
        help = "Path of a directory to save files")
    parser.add_argument("--lower", "-l",
        help = "(L)ower cased file extension, e.g.'.jpg'",
        action = "store_true")
    parser.add_argument("--upper", "-u",
        help = "(U)pper cased file extension, e.g.'.JPG'",
        action = "store_true")
    parser.add_argument("--dryrun", "-d",
        help = "Only print what {} will do".format(parser.prog),
        action = "store_true")
    parser.add_argument("--tzdelta",
        help = "Timezone delta where photos/videos taken in. e.g. '+9'")
    return(parser)

# check command arguments
def check_args(args) -> str:
    # set realpath, it can be a file or a directory
    # if realpath is a directory, this scripts find files under the directory with glob()
    # this behavior is a reason why I don't rely on exceptions
    input_realpath = os.path.realpath(args.input)
    if os.path.exists(input_realpath) == False:
        return("{}: No such file or directory\n".format(input_realpath))
    args.input_realpath = input_realpath

    # At least one argument is required
    if args.move == False and args.rename == False and args.camera == False:
        return("Nothing to do.\nPlease specify one of arguments, 'move', 'rename', or 'camera'.\n")

    # If output directory doesn't exist, ask whether to create or not
    if args.output != None:
        output_realpath = os.path.realpath(args.output)
        if os.path.exists(output_realpath) == False:
            print("\n" + "Could not find the directory '{}'. Do you want to create it? [Y/n]".format(output_realpath))
            while True:
                c = sys.stdin.read(1).lower()
                if c == "y" or ord(c) == 10:
                    os.makedirs(output_realpath)
                    args.output_realpath = output_realpath
                    return
                elif c == "n":
                    print("\n" + "Stopped processing." + "\n")
                    sys.exit(1)
                else:
                    print("\n" + "Please input Y or N.")
        else:
            args.output_realpath = output_realpath

# find 'image' or 'video' files
def classify_files(args) -> list[str]:
    # EXIF doesn't include timezone info.
    # Need to convert datetime in EXIF to one in local timezone.
    if args.tzdelta == None:
        tz = datetime.now().astimezone().tzinfo
    else:
        tz = timezone(timedelta(hours=int(args.tzdelta)))

    # find files
    if os.path.isdir(args.input_realpath) == True:
        files = [f for f in sorted(glob.glob(args.input_realpath + "/**", recursive = args.recursive)) if os.path.isfile(f) == True]
    else:
        files = [args.input_realpath]

    # make dictionary for new files to be created
    newfiles = []
    for f in files:
        # decide which file is to be processed
        mime = magic.from_file(f, mime=True)
        if mime in targeted_mime_types['image']:
            dtstr = subprocess.check_output(["mdls", "-name", "kMDItemContentCreationDate", "-raw", f]).decode()
            dt = datetime.strptime(dtstr, '%Y-%m-%d %H:%M:%S %z').astimezone(tz)
            cm = subprocess.check_output(["mdls", "-name", "kMDItemAcquisitionModel", "-raw", f]).decode()
        elif mime in targeted_mime_types['video']:
            dtstr = subprocess.check_output(["mdls", "-name", "kMDItemContentCreationDate", "-raw", f]).decode()
            dt = datetime.strptime(dtstr, '%Y-%m-%d %H:%M:%S %z').astimezone(tz)
            cm = "NONE"
        else: #Nothing to do for untargeted
            continue

        # make new directory name if needed
        if args.output != None:
            dirname = args.output_realpath
        else:
            dirname = args.input_realpath
        if args.move == True:
            dirname = dirname + dt.strftime("/%Y/%m/%d")
        if args.camera == True:
            dirname = dirname + "/" + cm

        # make new file name if needed
        if args.rename == True:
            newname = dt.strftime("%Y%m%d%H%M%S")
            newext = os.path.splitext(os.path.basename(f))[1]
        else:
            newname = os.path.splitext(os.path.basename(f))[0]
            newext = os.path.splitext(os.path.basename(f))[1]
        if args.lower == True:
            newext = newext.lower()
        if args.upper == True:
            newext = newext.upper()

        newfiles.append({'orig': f, 'dir': dirname, 'name': newname, 'ext': newext})

    # check duplication
    for i in range(1, len(newfiles) - 1):
        if ('seq' in newfiles[i]) == True:
            max = newfiles[i]['seq']
        else:
            max = 1
        for j in range(i + 1, len(newfiles)):
            if newfiles[i]['name'] == newfiles[j]['name']:
                if ('seq' in newfiles[i]) == False:
                    newfiles[i]['seq'] = 1
                max = max + 1
                newfiles[j]['seq'] = max
   
    # Execute
    for f in newfiles:
        # make directory
        try:
            if args.dryrun == False:
                os.path.makedir(f['dir'])
            else:
                print("mkdir -p {}".format(f['dir']))
        except:
            pass
        if args.move == True:
            if ('seq' in f) == True:
                if args.dryrun == False:
                    shutil.move(f['orig'], "{dir}/{name}-{seq}{ext}".format(dir=f['dir'], name=f['name'], seq=f['seq'], ext=f['ext']))
                else:
                    print("mv {orig} {dir}/{name}-{seq}{ext}".format(orig=f['orig'], dir=f['dir'], name=f['name'], seq=f['seq'], ext=f['ext']))
            else:
                if args.dryrun == False:
                    shutil.move(f['orig'], "{dir}/{name}{ext}".format(dir=f['dir'], name=f['name'], ext=f['ext']))
                else:
                    print("mv {orig} {dir}/{name}{ext}".format(orig=f['orig'], dir=f['dir'], name=f['name'], ext=f['ext']))
        else:
            if ('seq' in f) == True:
                if args.dryrun == False:
                    shutil.copy(f['orig'], "{dir}/{name}-{seq}{ext}".format(dir=f['dir'], name=f['name'], seq=f['seq'], ext=f['ext']))
                else:
                    print("cp {orig} {dir}/{name}-{seq}{ext}".format(orig=f['orig'], dir=f['dir'], name=f['name'], seq=f['seq'], ext=f['ext']))
            else:
                if args.dryrun == False:
                    shutil.copy(f['orig'], "{dir}/{name}{ext}".format(dir=f['dir'], name=f['name'], ext=f['ext']))
                else:
                    print("cp {orig} {dir}/{name}{ext}".format(orig=f['orig'], dir=f['dir'], name=f['name'], ext=f['ext']))
            
def main():
    # set arguments
    parser = set_args()

    # parse the arguments
    args = parser.parse_args()

    # check args and add input_realpath and output_realpath
    error = check_args(args)
    if error != None:
        print(error)
        parser.print_help()
        sys.exit()

    # glob files to be processed
    classify_files(args)

if __name__ == "__main__":
    main()