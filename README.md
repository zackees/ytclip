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


``` (Interactive)
$ cd <MY_DIRECTORY>
$ ytclip
Add new video:
  url: ...
  start_timestamp: 08:08
  length: 20
  output_name: my_file
```

``` (CMD-line)
$ cd <MY_DIRECTORY>
$ ytclip --url https://www.youtube.com/watch?v=CLXt3yh2g0s --start_timestamp 00:32 --length 20 --outname myoutputfile
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

You can also turn off logging like so:

```
from ytclip.ytclip import run_download_and_cut, set_logging

set_logging(False)
run_download_and_cut(...)
```