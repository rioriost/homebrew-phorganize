#!/usr/bin/env python3

import argparse
import asyncio
from datetime import datetime, timezone, timedelta
import glob
import magic
import os
import platform
import shutil
import subprocess
import sys
from typing import Optional


class MediaFile:
    """
    Each MediaFile object represents a file to be organized.
    It extracts mime type and metadata using magic and mdls commands.
    It generates target directory and file name based on the options and metadata.
    """

    # mime type to be targeted
    TARGETED_MIME_TYPES = [
        "image/jpeg",
        "image/heic",
        "image/png",
        "image/tiff",
        "image/x-canon-crw",
        "image/x-canon-cr2",
        "image/x-canon-cr3",
        "image/x-fuji-raf",
        "image/x-x3f",
        "image/x-olympus-orf",
        "video/mp4",
        "video/quicktime",
        "application/octet-stream",
    ]

    def __init__(self, file_path: str, tz: timezone):
        self.orig = file_path
        self.tz = tz
        self.mime = magic.from_file(file_path, mime=True)
        self.valid = False
        self.dt: Optional[datetime] = None
        self.camera: str = ""  # Annotate as Optional[str]
        self.target_dir: str = ""
        self.newname: str = ""
        self.ext: str = ""
        self.seq: int = 0  # sequence number for duplicate files
        self._extract_metadata()

    def _extract_metadata(self) -> None:
        """
        extract metadata from the file using mdls command.
        if the mime type is not targeted, valid flag will be False.

        Args:
            None

        Returns:
            None
        """
        try:
            if self.mime in self.TARGETED_MIME_TYPES:
                (self.camera, dt_str) = (
                    subprocess.check_output(
                        [
                            "mdls",
                            "-name",
                            "kMDItemAcquisitionModel",
                            "-name",
                            "kMDItemContentCreationDate",
                            "-raw",
                            self.orig,
                        ]
                    )
                    .decode()
                    .strip()
                    .split(chr(0))
                )
                self.dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S %z").astimezone(
                    self.tz
                )
                self.valid = True
        except Exception:
            self.valid = False

    def generate_target(self, args: argparse.Namespace, base_dir: str = "") -> None:
        """
        generate target directory and file name based on the options and extracted metadata.

        Args:
            base_dir: the base directory for the output file
            args: the argparse.Namespace object for the command line

        Returns:
            None
        """
        target_dir = base_dir
        if args.move and self.dt is not None:
            # create subdirectories for each date
            target_dir = os.path.join(
                target_dir,
                self.dt.strftime("%Y"),
                self.dt.strftime("%m"),
                self.dt.strftime("%d"),
            )
        if args.camera and self.camera is not None:
            target_dir = os.path.join(target_dir, self.camera)

        # generate file name (based on the original name or the date time)
        base_filename = (
            self.dt.strftime("%Y%m%d%H%M%S")
            if args.rename and self.dt is not None
            else os.path.splitext(os.path.basename(self.orig))[0]
        )
        ext = os.path.splitext(self.orig)[1]
        if args.lower:
            ext = ext.lower()
        if args.upper:
            ext = ext.upper()

        self.target_dir = target_dir
        self.newname = base_filename
        self.ext = ext

    def get_target_fullpath(self) -> str:
        """
        return the full path of the output file (with sequence number if exists).

        Args:
            None

        Returns:
            str: the full path of the output file
        """
        if self.seq != 0:
            filename = f"{self.newname}-{self.seq}{self.ext}"
        else:
            filename = f"{self.newname}{self.ext}"
        return os.path.join(self.target_dir, filename)


class FileOrganizer:
    """
    FileOrganizer class organizes photos and videos using embedded meta data in the files.
    It checks arguments, finds target files, builds MediaFile objects, assigns sequence numbers,
    """

    def __init__(self, args: argparse.Namespace) -> None:
        """
        initialize the FileOrganizer object with the command line arguments.

        Args:
            args: the argparse.Namespace object for the command line

        Returns:
            None
        """
        self.args = args
        self._set_timezone()
        self.input_realpath = os.path.realpath(args.input)
        if args.output:
            self.output_base = os.path.realpath(args.output)
        else:
            self.output_base = (
                os.path.dirname(self.input_realpath)
                if os.path.isfile(self.input_realpath)
                else self.input_realpath
            )
        self.media_files: list = []

    def _set_timezone(self) -> None:
        """
        if tzdelta is not specified, set the local timezone.
        if tzdelta is specified, set the timezone based on the delta.

        Args:
            None

        Returns:
            None
        """
        if self.args.tzdelta:
            try:
                delta = int(self.args.tzdelta)
            except ValueError:
                delta = 0
            self.tz = timezone(timedelta(hours=delta))
        else:
            current_tz = datetime.now().astimezone().tzinfo
            if isinstance(current_tz, timezone):
                self.tz = current_tz
            else:
                # Fallback to UTC if tzinfo isn’t an instance of timezone.
                self.tz = timezone.utc

    def check_paths(self) -> None:
        """
        check the existence of the input path and the output directory.

        Args:
            None

        Returns:
            None
        """
        if not os.path.exists(self.input_realpath):
            sys.exit(f"{self.input_realpath}: No such file or directory")
        if self.args.output:
            if not os.path.exists(self.output_base):
                answer = (
                    input(
                        f"Could not find the directory '{self.output_base}'. Do you want to create it? [Y/n] "
                    )
                    .strip()
                    .lower()
                )
                if answer in ("", "y"):
                    try:
                        os.makedirs(self.output_base, exist_ok=True)
                    except Exception as e:
                        sys.exit(f"Failed to create directory {self.output_base}: {e}")
                else:
                    sys.exit("Stopped processing.")

    def find_files(self) -> list:
        """
        if the input path is a directory, return the list of files in the directory.

        Args:
            None

        Returns:
            list: the list of files in the directory
        """
        if os.path.isdir(self.input_realpath):
            pattern = (
                os.path.join(self.input_realpath, "**", "*")
                if self.args.recursive
                else os.path.join(self.input_realpath, "*")
            )
            return [
                f
                for f in sorted(glob.glob(pattern, recursive=self.args.recursive))
                if os.path.isfile(f)
            ]
        else:
            return [self.input_realpath]

    async def build_media_files(self) -> None:
        """
        generate MediaFile objects from the list of files.
        heavy processes like mdls are executed asynchronously in parallel using asyncio.to_thread.

        Args:
            None

        Returns:
            None
        """
        files = self.find_files()
        tasks = [asyncio.to_thread(self._create_media_file, file_path=f) for f in files]
        results = await asyncio.gather(*tasks)
        # 有効な MediaFile のみ保持し、ターゲット生成も行う
        for mf in results:
            if mf and mf.valid:
                mf.generate_target(base_dir=self.output_base, args=self.args)
                self.media_files.append(mf)

    def _create_media_file(self, file_path: str = "") -> MediaFile:
        """
        create a MediaFile object from the file path.

        Args:
            file_path: the file path

        Returns:
            MediaFile: the MediaFile object
        """
        mf = MediaFile(file_path=file_path, tz=self.tz)
        return mf

    def assign_duplicate_sequence(self) -> None:
        """
        Group files by newname, and if there are multiple files with the same newname,
        assign a sequence number starting from 1 to the duplicates.
        The first file in each group gets sequence number 0 (indicating no sequence suffix).

        Args:
            None

        Returns:
            None
        """
        groups: dict = {}
        # Group MediaFile objects by their newname.
        for mf in self.media_files:
            groups.setdefault(mf.newname, []).append(mf)

        # For each group, assign sequence numbers.
        for group in groups.values():
            if len(group) > 1:
                for index, mf in enumerate(group):
                    # The first file gets 0 (no sequence appended),
                    # subsequent files get sequence numbers starting from 1.
                    mf.seq = index + 1
            else:
                group[0].seq = 0

    async def process_media_file(self, mf: MediaFile) -> None:
        """
        create a directory for the MediaFile object and move or copy the file to the directory.
        if dryrun is specified, only print the command.

        Args:
            mf: the MediaFile object

        Returns:
            None
        """
        # ディレクトリ作成（dryrun時は表示のみ）
        if not self.args.dryrun:
            await asyncio.to_thread(os.makedirs, mf.target_dir, exist_ok=True)
        else:
            print(f"mkdir -p {mf.target_dir}")

        target_fullpath = mf.get_target_fullpath()
        if self.args.move:
            if not self.args.dryrun:
                await asyncio.to_thread(shutil.move, mf.orig, target_fullpath)
            else:
                print(f"mv {mf.orig} {target_fullpath}")
        else:
            if not self.args.dryrun:
                await asyncio.to_thread(shutil.copy, mf.orig, target_fullpath)
            else:
                print(f"cp {mf.orig} {target_fullpath}")

    async def execute(self) -> None:
        """
        execute the final file processing.
        1. build MediaFile objects (asynchronously in parallel)
        2. assign sequence numbers
        3. execute moving/copying each file asynchronously

        Args:
            None

        Returns:
            None
        """
        print(f"Processing files in {self.input_realpath}...")
        await self.build_media_files()
        self.assign_duplicate_sequence()

        tasks = [self.process_media_file(mf) for mf in self.media_files]
        await asyncio.gather(*tasks)
        print("Done.")


def parse_args() -> argparse.Namespace:
    """
    parse command line arguments.

    Args:
        None

    Returns:
        argparse.Namespace: the argparse.Namespace object for the command line
    """
    parser = argparse.ArgumentParser(
        description="Organize photos and videos using embedded meta data in the files"
    )
    parser.add_argument(
        "input", help="Input path of photos and videos or directory to find them"
    )
    parser.add_argument(
        "--verbose", "-v", help="increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "--move",
        "-m",
        help="(M)ove files to sub-directories, not copy",
        action="store_true",
    )
    parser.add_argument(
        "--rename",
        "-r",
        help="(R)ename files, NOT maintain original name",
        action="store_true",
    )
    parser.add_argument(
        "--recursive",
        help="Find files recursively within input directory",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--camera",
        "-c",
        help="make sub-directories with (C)amera model",
        action="store_true",
    )
    parser.add_argument("--output", "-o", help="Path of a directory to save files")
    parser.add_argument(
        "--lower",
        "-l",
        help="(L)ower cased file extension, e.g. '.jpg'",
        action="store_true",
    )
    parser.add_argument(
        "--upper",
        "-u",
        help="(U)pper cased file extension, e.g. '.JPG'",
        action="store_true",
    )
    parser.add_argument(
        "--dryrun",
        "-d",
        help="Only print what the program will do",
        action="store_true",
    )
    parser.add_argument(
        "--tzdelta", help="Timezone delta where photos/videos taken in. e.g. '+9'"
    )
    args = parser.parse_args()

    if not (args.move or args.rename or args.camera):
        parser.error(
            "Nothing to do. Please specify one of arguments, 'move', 'rename', or 'camera'."
        )
    return args


def check_platform() -> None:
    """
    check the platform is Apple Silicon Mac.

    Args:
        None

    Returns:
        None
    """
    if sys.platform != "darwin" or platform.machine() != "arm64":
        sys.exit("This program is only for Apple Silicon Mac.")


async def async_main():
    check_platform()
    args = parse_args()
    organizer = FileOrganizer(args)
    organizer.check_paths()
    await organizer.execute()


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
