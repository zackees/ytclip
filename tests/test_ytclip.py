import os
import unittest


class YtclipTester(unittest.TestCase):

    def test_imports(self) -> None:
        from ytclip.ytclip import run_download_and_cut
        self.assertTrue(run_download_and_cut)

    def test_platform_executable(self) -> None:
        rtn = os.system('ytclip --version')
        self.assertEqual(0, rtn)


if __name__ == "__main__":
    unittest.main()
