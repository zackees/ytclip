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

### Windows

For easy use, download the [`run_ytclip.bat`](https://raw.githubusercontent.com/zackees/ytclip/main/run_ytclip.bat) and place it into any folder you want. Now you have a double clickable icon
for users that don't like going to the command line. If it doesn't work, make sure you've installed the latest python [link](https://python.org/download).

# Running


``` (Interactive)
$ cd <MY_DIRECTORY>
$ ytclip
Add new video:
  url: ...
  start_timestamp: 08:08
  end_timestamp: 08:20
  output_name: my_file
```

``` (CMD-line)
$ cd <MY_DIRECTORY>
$ ytclip https://www.youtube.com/watch?v=CLXt3yh2g0s --start_timestamp 00:32 --end_timestamp 00:52 --outname myoutputfile
```

``` Help file
$ ytclip --help
```


# Api

You can also use it as an api:

```
from ytclip.ytclip import run_download_and_cut

run_download_and_cut(
    url="https://www.youtube.com/watch?v=-wtIMTCHWuI",
    start_timestamp="1:10",
    end_timestamp="1:30",
    outname="myclip_withoutsuffix")
```

You can also turn off logging like so:

```
from ytclip.ytclip import run_download_and_cut, set_logging

set_logging(False)
run_download_and_cut(...)
```
