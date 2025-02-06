#!/usr/bin/env python3
import argparse
import os
import sys
import unittest
from datetime import datetime, timezone, timedelta
from io import StringIO
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from phorganize.main import MediaFile, FileOrganizer


#######################################################################
# Synchronous tests for MediaFile
#######################################################################
class TestMediaFile(unittest.TestCase):
    def setUp(self):
        # Dummy file path (actual existence is not required)
        self.dummy_path = "dummy.jpg"
        # Testing timezone (+9:00)
        self.tz = timezone(timedelta(hours=9))

    @patch("magic.from_file")
    @patch("subprocess.check_output")
    def test_extract_metadata_success(self, mock_check_output, mock_from_file):
        # Simulate mdls command output:
        # Camera model and creation date are separated by a NULL character.
        mdls_output = b"Canon\x002023-01-01 12:00:00 +0900"
        mock_check_output.return_value = mdls_output
        # Return a MIME type that is targeted.
        mock_from_file.return_value = "image/jpeg"

        mf = MediaFile(file_path=self.dummy_path, tz=self.tz)
        self.assertTrue(mf.valid)
        self.assertEqual(mf.camera, "Canon")
        expected_dt = datetime.strptime(
            "2023-01-01 12:00:00 +0900", "%Y-%m-%d %H:%M:%S %z"
        ).astimezone(self.tz)
        self.assertEqual(mf.dt, expected_dt)

    def test_extract_metadata_fail_non_target_mime(self):
        # If a non-targeted MIME type is provided, valid should be False.
        with patch("magic.from_file", return_value="application/pdf"):
            mf = MediaFile(file_path=self.dummy_path, tz=self.tz)
            self.assertFalse(mf.valid)

    @patch("magic.from_file")
    @patch("subprocess.check_output")
    def test_generate_target(self, mock_check_output, mock_from_file):
        # Simulate mdls output.
        mdls_output = b"Nikon\x002023-05-15 10:30:00 +0900"
        mock_check_output.return_value = mdls_output
        mock_from_file.return_value = "image/jpeg"

        # Use "Picture.PNG" to verify extension conversion.
        mf = MediaFile(file_path="Picture.PNG", tz=self.tz)
        self.assertTrue(mf.valid)

        # Create an argparse.Namespace as required by generate_target.
        args = argparse.Namespace(
            move=True,
            rename=True,
            camera=True,
            lower=True,
            upper=False,
            dryrun=False,
            recursive=False,
            output="output_dir",
            tzdelta=None,
            input="dummy_input",
            verbose=False,
        )
        mf.generate_target(args=args, base_dir="output_dir")
        dt = mf.dt  # 2023-05-15 10:30:00 +0900
        expected_dir = os.path.join(
            "output_dir",
            dt.strftime("%Y"),
            dt.strftime("%m"),
            dt.strftime("%d"),
            mf.camera,
        )
        self.assertEqual(mf.target_dir, expected_dir)
        expected_basename = dt.strftime("%Y%m%d%H%M%S")
        self.assertEqual(mf.newname, expected_basename)
        # Due to lower=True, the file extension should be lowercase.
        self.assertEqual(mf.ext, ".png")

    def test_get_target_fullpath_with_sequence(self):
        mf = MediaFile(file_path="dummy.jpg", tz=self.tz)
        mf.target_dir = "output_dir"
        mf.newname = "testfile"
        mf.ext = ".jpg"
        mf.seq = 2
        fullpath = mf.get_target_fullpath()
        expected = os.path.join("output_dir", "testfile-2.jpg")
        self.assertEqual(fullpath, expected)

    def test_get_target_fullpath_without_sequence(self):
        mf = MediaFile(file_path="dummy.jpg", tz=self.tz)
        mf.target_dir = "output_dir"
        mf.newname = "testfile"
        mf.ext = ".jpg"
        mf.seq = None
        fullpath = mf.get_target_fullpath()
        # In the code, if seq is not None, a suffix is appended, so with None, "-None" is appended.
        expected = os.path.join("output_dir", "testfile-None.jpg")
        self.assertEqual(fullpath, expected)


#######################################################################
# Synchronous tests for FileOrganizer
#######################################################################
class TestFileOrganizerSync(unittest.TestCase):
    def setUp(self):
        self.args = argparse.Namespace(
            move=True,
            rename=True,
            camera=True,
            lower=True,
            upper=False,
            dryrun=True,  # In dryrun mode, actual file operations are not performed.
            recursive=False,
            output="output_dir",
            tzdelta=None,
            input="dummy_input",
            verbose=False,
        )
        self.organizer = FileOrganizer(self.args)
        self.organizer.tz = timezone(timedelta(hours=9))

    def test_assign_duplicate_sequence(self):
        # Create MediaFile objects with duplicate and unique newname values.
        mf1 = MediaFile(file_path="dummy1.jpg", tz=self.organizer.tz)
        mf1.newname = "duplicate"
        mf2 = MediaFile(file_path="dummy2.jpg", tz=self.organizer.tz)
        mf2.newname = "duplicate"
        mf3 = MediaFile(file_path="dummy3.jpg", tz=self.organizer.tz)
        mf3.newname = "unique"
        self.organizer.media_files = [mf1, mf2, mf3]

        self.organizer.assign_duplicate_sequence()

        # For the "duplicate" group (more than one file), the sequence numbers are assigned as index+1.
        # So the first duplicate gets seq=1 and the second gets seq=2.
        self.assertEqual(mf1.seq, 1)
        self.assertEqual(mf2.seq, 2)
        # For "unique" group (only one file), the method does not change the sequence,
        # so it should remain 0.
        self.assertEqual(mf3.seq, 0)

    def test_check_paths_input_missing(self):
        # When the input path does not exist, check_paths() should call sys.exit.
        with patch("os.path.exists", return_value=False):
            with self.assertRaises(SystemExit):
                self.organizer.check_paths()


#######################################################################
# Asynchronous tests for FileOrganizer
#######################################################################
class TestFileOrganizerAsync(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Create an organizer instance for asynchronous tests.
        self.args = argparse.Namespace(
            move=False,  # Test the copy operation.
            rename=True,
            camera=True,
            lower=True,
            upper=False,
            dryrun=True,
            recursive=False,
            output="output_dir",
            tzdelta=None,
            input="dummy_input",
            verbose=False,
        )
        self.organizer = FileOrganizer(self.args)
        self.organizer.tz = timezone(timedelta(hours=9))

    async def test_process_media_file_dryrun_copy(self):
        # Verify that process_media_file behaves correctly in dryrun mode (copy operation).
        mf = MediaFile(file_path="dummy.jpg", tz=timezone(timedelta(hours=9)))
        mf.target_dir = os.path.join("output_dir", "2023", "05", "15", "Canon")
        mf.newname = "20230515123000"
        mf.ext = ".jpg"
        mf.seq = None  # First file so seq is None.
        expected_fullpath = os.path.join(mf.target_dir, f"{mf.newname}-None.jpg")
        captured_output = StringIO()
        with patch("sys.stdout", new=captured_output):
            await self.organizer.process_media_file(mf)
        output = captured_output.getvalue()
        expected_mkdir = f"mkdir -p {mf.target_dir}"
        expected_cp = f"cp {mf.orig} {expected_fullpath}"
        self.assertIn(expected_mkdir, output)
        self.assertIn(expected_cp, output)

    async def test_build_media_files(self):
        # Fix the return value of find_files() to verify that _create_media_file is called correctly.
        file_list = ["dummy1.jpg", "dummy2.jpg"]
        organizer = self.organizer
        with (
            patch.object(organizer, "find_files", return_value=file_list),
            patch.object(organizer, "_create_media_file") as mock_create_media_file,
        ):

            def fake_create(file_path):
                mf = MediaFile(file_path=file_path, tz=organizer.tz)
                mf.valid = True  # Mark the file as valid.
                mf.dt = datetime.now(organizer.tz)
                mf.camera = "FakeCamera"
                return mf

            mock_create_media_file.side_effect = fake_create

            await organizer.build_media_files()
            self.assertEqual(len(organizer.media_files), len(file_list))
            for mf in organizer.media_files:
                self.assertTrue(hasattr(mf, "target_dir"))
                self.assertTrue(hasattr(mf, "newname"))
                self.assertTrue(hasattr(mf, "ext"))


if __name__ == "__main__":
    unittest.main()
