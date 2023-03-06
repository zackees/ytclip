import os
import unittest
import tempfile
import subprocess
import sys


from ytclip.ytclip import run_download_and_cut

class YtclipTester(unittest.TestCase):

    def test_imports(self) -> None:
        from ytclip.ytclip import run_download_and_cut
        self.assertTrue(run_download_and_cut)

    def test_platform_executable(self) -> None:
        rtn = os.system('ytclip --version')
        self.assertEqual(0, rtn)

    def test_notimestamps_cmd(self) -> None:
        # Create a temporary directory where the file will be saved
        with tempfile.TemporaryDirectory() as tmpdir:
            outname = os.path.join(tmpdir, "test")
            cmd = f'ytclip https://www.youtube.com/watch?v=oG25KSvFEq0 --start_time "" --end_time "" --outname "{outname}"'
            rtn = os.system(cmd)
            self.assertEqual(0, rtn)

    def test_notimestamps(self) -> None:
        # Create a temporary directory where the file will be saved
        with tempfile.TemporaryDirectory() as tmpdir:
            outname = os.path.join(tmpdir, "test")
            run_download_and_cut(url="https://www.youtube.com/watch?v=oG25KSvFEq0", start_timestamp="", end_timestamp="", outname=outname, verbose=True, keep=False, log=True)
            os.path.exists(outname)

    def test_yttime_value(self) -> None:
        # Create a temporary directory where the file will be saved
        with tempfile.TemporaryDirectory() as tmpdir:
            outname = os.path.join(tmpdir, "test")
            run_download_and_cut(url="https://www.youtube.com/watch?v=oG25KSvFEq0?t=1", start_timestamp="", end_timestamp="", outname=outname, verbose=True, keep=False, log=True)
            os.path.exists(outname)
            


if __name__ == "__main__":
    unittest.main()
