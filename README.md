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