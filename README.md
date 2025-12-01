# Phorganize

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)

## Overview

Phorganize is a python script to organize photos and videos using embedded meta data in the files.
It can move files to sub-directories, rename files, and make sub-directories with camera model if you specify the options.
It runs on macOS.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

Just add tap and install homebrew package.

```bash
brew tap rioriost/phorganize
brew install phorganize
```

## Usage

Execute phorganize command.

```bash
phorganize --help
usage: phorganize [-h] [--verbose] [--move] [--rename] [--recursive] [--camera] [--output OUTPUT] [--lower] [--upper] [--dryrun] [--tzdelta TZDELTA] input

Organize photos and videos using embedded meta data in the files

positional arguments:
  input                 Input path of photos and videos or directory to find them

options:
  -h, --help            show this help message and exit
  --verbose, -v         increase output verbosity
  --move, -m            (M)ove files to sub-directories, not copy
  --rename, -r          (R)ename files, NOT maintain original name
  --recursive           Find files recursively within input directory
  --camera, -c          make sub-directories with (C)amera model
  --output OUTPUT, -o OUTPUT
                        Path of a directory to save files
  --lower, -l           (L)ower cased file extension, e.g. '.jpg'
  --upper, -u           (U)pper cased file extension, e.g. '.JPG'
  --dryrun, -d          Only print what the program will do
  --tzdelta TZDELTA     Timezone delta where photos/videos taken in. e.g. '+9'
```

The indentical usage is shown below.

e.g. a directory named 'photos' contains photos and videos.

```bash
tree ~/Desktop/photos
/Users/rifujita/Desktop/photos
├── 125A9549.MP4
├── 125A9550.CR3
├── 125A9551.CR3
├── 125A9552.CR3
├── 125A9553.CR3
├── 125A9657.CR3
├── 125A9658.CR3
├── 125A9724.MP4
├── 125A9725.CR3
├── 125A9730.CR3
├── 20160507120409.CR2
├── 20210710173257.dng
├── 20220627170828.CR2
├── 20220627170829.CR2
├── 2023120110.MP4
├── IMG_9873.HEIC
├── IMG_9874.HEIC
└── IMG_9875.HEIC

1 directory, 18 files
```

```bash
phorganize -r -c -m ~/Desktop/photos
Processing files in /Users/rifujita/Desktop/photos...
Done.
```

* -r: Rename files, NOT maintain original name. Renaming is a little bit dangerous, so PLEASE USE IT CAREFULLY.
* -m: Move files to sub-directories, not copy
* -c: Make sub-directories with camera model

After phorganize is executed, the directory 'photos' is organized as shown below.

```bash
tree ~/Desktop/photos
/Users/rifujita/Desktop/photos
├── 2016
│   └── 05
│       └── 07
│           └── Canon PowerShot S120
│               └── 20160507120409.CR2
├── 2021
│   └── 07
│       └── 10
│           └── iPhone 11 Pro
│               └── 20210710173257.dng
├── 2022
│   └── 06
│       └── 27
│           └── Canon EOS 5D Mark III
│               ├── 20220627170828.CR2
│               └── 20220627170829.CR2
├── 2023
│   └── 12
│       └── 01
│           └── (null)
│               └── 20231201101539.MP4
└── 2025
    └── 02
        └── 06
            ├── (null)
            │   ├── 20250206181442.MP4
            │   └── 20250206185300.MP4
            ├── Canon EOS R6m2
            │   ├── 20250206181616-1.CR3
            │   ├── 20250206181616-2.CR3
            │   ├── 20250206181616-3.CR3
            │   ├── 20250206181616-4.CR3
            │   ├── 20250206183628-1.CR3
            │   ├── 20250206183628-2.CR3
            │   ├── 20250206185925-1.CR3
            │   └── 20250206185925-2.CR3
            └── iPhone 16 Pro
                ├── 20250206180947-1.HEIC
                ├── 20250206180947-2.HEIC
                └── 20250206180948.HEIC

23 directories, 18 files
```

If multiple files will have the same new name, phorganize will add a sequence number to the file name.
Movie files do not have camera model information, so they are organized in the '(null)' directory.

## Release Notes

### 0.1.3 Release
* Security update

### 0.1.2 Release
* Updated for the dependencies.

### 0.1.1 Release
* Fixed a title of README.md

### 0.1.0 Release
* First release.

## License
MIT License
