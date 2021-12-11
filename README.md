# homebrew-phorganize
Organize the photos and the videos using embedded meta data in the files

It can run only on macOS because of dependency on 'mdls' command.
Please use this script at your own risk after careful reading the help and the descriptions below.

## Install
```
brew tap rioriost/phorganize
brew install rioriost/phorganize/homebrew-phorganize
```

## Usage
```
usage: phorganize [-h] [--verbose] [--move] [--rename] [--recursive] [--camera] [--output OUTPUT] [--lower] [--upper] [--dryrun] [--tzdelta TZDELTA] input

Organize the photos and the videos using embedded meta data in the files

positional arguments:
  input                 Input path of photos and videos or directory to find them

optional arguments:
  -h, --help            show this help message and exit
  --verbose, -v         increase output (V)erbosity
  --move, -m            (M)ove files to sub-directories, not copy
  --rename, -r          (R)ename files, NOT maintain original name
  --recursive           Find files recursively within input directory
  --camera, -c          make sub-directories with (C)amera model
  --output OUTPUT, -o OUTPUT
                        Path of a directory to save files
  --lower, -l           (L)ower cased file extension, e.g.'.jpg'
  --upper, -u           (U)pper cased file extension, e.g.'.JPG'
  --dryrun, -d          Only print what phorganize will do
  --tzdelta TZDELTA     Timezone delta where photos/videos taken in. e.g. '+9'
```


## The safer usage

--dryrun is useful to check what will happen for the files you specified.

```
% phorganize --dryrun -r Desktop/test
mkdir -p /Users/rifujita/Desktop/test
cp /Users/rifujita/Desktop/test/IMG_4187.JPG /Users/rifujita/Desktop/test/20211005104727.JPG
mkdir -p /Users/rifujita/Desktop/test
cp /Users/rifujita/Desktop/test/IMG_4188.JPG /Users/rifujita/Desktop/test/20211005104804.JPG
mkdir -p /Users/rifujita/Desktop/test
cp /Users/rifujita/Desktop/test/IMG_4212.JPG /Users/rifujita/Desktop/test/20211011104028.JPG
mkdir -p /Users/rifujita/Desktop/test
cp /Users/rifujita/Desktop/test/IMG_4213.JPG /Users/rifujita/Desktop/test/20211011104106.JPG
mkdir -p /Users/rifujita/Desktop/test
cp /Users/rifujita/Desktop/test/IMG_4241.JPG /Users/rifujita/Desktop/test/20211031121531.JPG
mkdir -p /Users/rifujita/Desktop/test
cp /Users/rifujita/Desktop/test/IMG_4242.JPG /Users/rifujita/Desktop/test/20211031122207.JPG
```

## Options
--move, -m option moves the files. This is a little bit dangerous option, there's possibility that the files vanish. I guess you know the differences between 'cp' and 'mv' commands.

--rename, -r option copies the files with the new name based-on EXIF data in the files themselves. e.g. IMG_4242.JPG -> 20211031122207.JPG

--camera, -c makes sub-directories having the camera model name based-on EXIF data in the files.

You can combine the above 3 options, but you can not omit all of them.

```
###### move only
% phorganize --dryrun -m Desktop/test
mkdir -p /Users/rifujita/Desktop/test/2021/10/05
mv /Users/rifujita/Desktop/test/IMG_4187.JPG /Users/rifujita/Desktop/test/2021/10/05/IMG_4187.JPG

###### rename only
% phorganize --dryrun -r Desktop/test
mkdir -p /Users/rifujita/Desktop/test
cp /Users/rifujita/Desktop/test/IMG_4187.JPG /Users/rifujita/Desktop/test/20211005104727.JPG

###### camera only
% phorganize --dryrun -c Desktop/test
mkdir -p /Users/rifujita/Desktop/test/iPhone 11 Pro
cp /Users/rifujita/Desktop/test/IMG_4187.JPG /Users/rifujita/Desktop/test/iPhone 11 Pro/IMG_4187.JPG

###### move + rename
% phorganize --dryrun -mr Desktop/test
mkdir -p /Users/rifujita/Desktop/test/2021/10/05
mv /Users/rifujita/Desktop/test/IMG_4187.JPG /Users/rifujita/Desktop/test/2021/10/05/20211005104727.JPG

###### move + camera
% phorganize --dryrun -mc Desktop/test
mkdir -p /Users/rifujita/Desktop/test/2021/10/05/iPhone 11 Pro
mv /Users/rifujita/Desktop/test/IMG_4187.JPG /Users/rifujita/Desktop/test/2021/10/05/iPhone 11 Pro/IMG_4187.JPG

###### rename + camera
% phorganize --dryrun -rc Desktop/test
mkdir -p /Users/rifujita/Desktop/test/iPhone 11 Pro
cp /Users/rifujita/Desktop/test/IMG_4187.JPG /Users/rifujita/Desktop/test/iPhone 11 Pro/20211005104727.JPG

###### all, rename + camera + move
% phorganize --dryrun -rmc Desktop/test
mkdir -p /Users/rifujita/Desktop/test/2021/10/05/iPhone 11 Pro
mv /Users/rifujita/Desktop/test/IMG_4187.JPG /Users/rifujita/Desktop/test/2021/10/05/iPhone 11 Pro/20211005104727.JPG
```


With --output, -o option, this script copy the files into the another directory, not input directory. This is one of the safer options.

--recursive may find more files under the directory you specified as an input.

--lower, -l / --upper, -u: If you're a little nervous about the character case of file extensions, it unifies them. e.g. JPG or jpg

--tzdelta can help you to manage the photos taken during oversea travel.

Unfortunately, EXIF doesn't support timezone, so you may find the photo describing that you took lunch at midnight. e.g. If you visited Tokyo, Japan, --tzdelta "+9" will change the filenames as a format 'yyyy/mm/dd/HH/MM/SS' in a local timezone you live in.
