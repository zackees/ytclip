import os
import stat
import subprocess
import sys
import unittest


class YtclipTester(unittest.TestCase):

    def test_platform_executable(self) -> None:
        rtn = os.system('ytclip --version')
        self.assertEqual(0, rtn)


if __name__ == "__main__":
    unittest.main()
