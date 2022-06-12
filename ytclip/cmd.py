"""
Command line utility for downloading and cutting videos.
"""

import os
import argparse
from ytclip.ytclip import run_download_and_cut, run_concurrent

from ytclip.version import VERSION


def _epilog() -> str:
    return (
        "Example:\n"
        "  ytclip https://www.youtube.com/watch?v=CLXt3yh2g0s --start_timestamp 00:32 --end_timestamp 00:58 --outname myoutputfile\n"  # pylint: disable=line-too-long
        "Any missing arguments will be prompted.\n"
    )


def run() -> int:  # pylint: disable=too-many-branches,too-many-statements
    """Entry point for the command line "ytclip" utilitiy."""

    parser = argparse.ArgumentParser(
        description="Downloads and clips videos from the internet.\n",
        epilog=_epilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="store_true", help=f"print version {VERSION}"
    )
    parser.add_argument("url", help="url of the video to download", nargs="?")
    parser.add_argument(
        "--concurrent", "-c", action="store_true", help="Allows multiple jobs"
    )
    parser.add_argument("--no-log", action="store_true", help="Suppresses logging.")
    parser.add_argument(
        "--start_timestamp", help="start timestamp of the clip", default=None
    )
    parser.add_argument(
        "--end_timestamp", help="end timestamp of the clip", default=None
    )
    parser.add_argument("--outname", help="output name of the file (auto saved as mp4)")
    parser.add_argument("--keep", action="store_true", help="keeps intermediate files")
    args = parser.parse_args()
    if args.version:
        print(f"{VERSION}")
        return 0

    if args.concurrent:
        run_concurrent()
        return 0
    url = args.url or input("url: ")
    start_timestamp = args.start_timestamp
    if start_timestamp is None:
        start_timestamp = input("start_timestamp: ")
    start_timestamp = start_timestamp or ""
    end_timestamp = args.end_timestamp
    if end_timestamp is None:
        end_timestamp = input("end_timestamp: ")
    end_timestamp = end_timestamp or ""
    while True:
        outname = args.outname or input("output name (auto saved as mp4): ")
        if outname != "":
            break
        print("Please enter a valid name")
    run_download_and_cut(
        url=url,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        outname=outname,
        verbose=True,
        keep=args.keep,
        log=not args.no_log,
    )
    if os.path.exists(f"{outname}.mp4"):
        return 0
    print(f"Download for {outname} failed")
    return 1


def main():
    """Just defaults to run_cmd."""
    run()


if __name__ == "__main__":
    # unit_test_brighteon()
    # unit_test_stdout_parse()
    # unit_test_bitchute()
    # unit_test_rap_video()
    main()
