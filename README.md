# ytclip

[![Actions Status](https://github.com/zackees/ytclip/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/ytclip/actions/workflows/push_macos.yml)
[![Actions Status](https://github.com/zackees/ytclip/workflows/Win_Tests/badge.svg)](https://github.com/zackees/ytclip/actions/workflows/push_win.yml)
[![Actions Status](https://github.com/zackees/ytclip/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/ytclip/actions/workflows/push_ubuntu.yml)

This utility provides a command that will automate downloading files and creating clips out of them.

The utility is user friendly.

It relies on `yt-dlp` to do the downloading of files and uses `static_ffmpeg` to do the actual cutting. This
stack should be cross platform and should not require elevated permissions to install (yay!).

# Install

```
$ python -m pip install ytclip
```

# Running

```
$ cd <MY_DIRECTORY>
$ ytclip
Add new video:
  url: ...
  start_timestamp: 08:08
  length: 20
  output_name: my_file
```

# In automation

To use this tool in your command scripts, pass the `--once` flag like `ytclip --once`. This allows the tool to only prompt the user once for input. The arguments will need to be passed into the command as stdin. For example something like this for bash:
```
    (echo 'http://www.youtube.com/watch?v=-wtIMTCHWuI'; echo '08:59'; echo '15'; echo './myoutput') | ytclip --once
```

# Api

You can also use it as an api:

```
from ytclip.ytclip import run_download_and_cut

run_download_and_cut(
    url="https://www.youtube.com/watch?v=-wtIMTCHWuI",
    start_timestamp="1:10",
    length="20",
    outname="myclip_withoutsuffix")
```