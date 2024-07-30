

import os
import unittest
import tempfile
import subprocess


DRM_URL = "https://www.youtube.com/watch?v=VTqTpGXlHms"

class YtclipDrmTester(unittest.TestCase):



    def test_notimestamps_cmd(self) -> None:
        # Create a temporary directory where the file will be saved
        with tempfile.TemporaryDirectory() as tmpdir:
            outname = os.path.join(tmpdir, "test")
            cmd = f'ytclip {DRM_URL} --start_time "" --end_time "" --outname "{outname}"'
            # rtn = os.system(cmd)
            cp = subprocess.run(cmd, shell=True, check=False, capture_output=True)
            self.assertIn("drm", cp.stderr.decode().lower())


if __name__ == "__main__":
    unittest.main()
