# ytclip - Quickly clip any video you see online and save it to your harddrive

# Usage

Make sure python (>3.7) is installed on your system.

```bash
> pip install ytclip
> ytclip https://www.youtube.com/watch?v=dQw4w9WgXcQ
# Follow the prompts
```

[![Actions Status](https://github.com/zackees/ytclip/workflows/MacOS_Tests/badge.svg)](https://github.com/zackees/ytclip/actions/workflows/push_macos.yml)
[![Actions Status](https://github.com/zackees/ytclip/workflows/Win_Tests/badge.svg)](https://github.com/zackees/ytclip/actions/workflows/push_win.yml)
[![Actions Status](https://github.com/zackees/ytclip/workflows/Ubuntu_Tests/badge.svg)](https://github.com/zackees/ytclip/actions/workflows/push_ubuntu.yml)

# About

This utility provides a command that will automate downloading files and creating clips out of them.

Uses `yt-dlp` to do the downloading of files and uses `static_ffmpeg` to do the actual cutting.

### Windows

For easy use, just download the [`run_ytclip.bat`](https://raw.githubusercontent.com/zackees/ytclip/main/run_ytclip.bat) file and place it into any folder you want. Now you have a double clickable icon for users that don't like going to the command line. Make sure you've installed the [latest python](https://python.org/download), checking the box that says "ADD TO PATH" during installation.

# Running


```bash
# (Interactive)
> cd <MY_DIRECTORY>
> ytclip
Add new video:
  url: ...
  start_timestamp: 08:08
  end_timestamp: 08:20
  output_name: my_file
```

```bash
# (CMD-line)
> cd <MY_DIRECTORY>
> ytclip https://www.youtube.com/watch?v=CLXt3yh2g0s --start_timestamp 00:32 --end_timestamp 00:52 --outname myoutputfile
```

```bash
# Help file
> ytclip --help
```


# Api

You can also use it as an api:

```python
from ytclip.ytclip import run_download_and_cut

run_download_and_cut(
    url="https://www.youtube.com/watch?v=-wtIMTCHWuI",
    start_timestamp="1:10",
    end_timestamp="1:30",
    outname="myclip_withoutsuffix")
```

You can also turn off logging like so:

```python
from ytclip.ytclip import run_download_and_cut, set_logging

set_logging(False)
run_download_and_cut(...)
```

# Server

See the server version: [ytclip-server](https://github.com/zackees/ytclip-server)

# Releases

  * 1.2.10: Adds `--crf` to control bit rate encoding.
  * 1.2.9: Drm video now detected properly and an output error message is emitted.
  * 1.2.8: Minimum version of `yt-dlp` bumped. Adds `--upgrade` for upgrading `yt-dlp`
  * 1.2.7: Brighteon downloads have been fixed, thanks to the brighteon plugin.
  * 1.2.6: Fix error where omitting length would cause error.
  * 1.2.5: Cleans youtube videos by removing the ?t= part of the url.
  * 1.2.4: Adds update warning for ytclip if out of date.
  * 1.2.3: Make yt-dlp use 1.2.3 or higher (fixes downloader).

# TODO

  * Add lossless cut to tool:
    * https://github.com/mifi/lossless-cut
