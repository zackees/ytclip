"""
    Downloads and clips videos from youtube, rumble, bitchute (using yt-dlp) and clips
    the video using ffmpeg.
"""

import os
import argparse
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple

from ytclip.version import VERSION

LOG = True
KEEP = False


def set_logging(val: bool) -> None:
    """Sets the logging state, which is the file created for each command."""
    global LOG  # pylint: disable=global-statement
    LOG = val


def _find_video_file_from_stdout(stdout: str) -> Optional[str]:
    value = None
    for line in stdout.splitlines():
        # File pattern # 1
        needle = '[Merger] Merging formats into "'
        if needle in line:
            value = line.replace(needle, "").replace('"', "")
            continue
        # File pattern # 2 (found in brighteon)
        needle = "[download] Destination: "
        if needle in line:
            value = line.replace(needle, "")
            continue
    return value


def _exec(
    cmd_str: str, verbose: bool = False, cwd: Optional[str] = None
) -> Tuple[int, str, str]:
    if verbose:
        sys.stdout.write(f'Running "{cmd_str}"\n')
    proc_yt = subprocess.Popen(  # pylint: disable=consider-using-with
        cmd_str,
        shell=True,
        cwd=cwd,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc_yt.communicate()
    if verbose:
        sys.stdout.write(stdout)
        sys.stderr.write(stderr)
    assert proc_yt.returncode is not None
    return proc_yt.returncode, stdout, stderr


def _append_file(filepath: str, data: str):
    with open(filepath, encoding="utf-8", mode="a+") as filed:
        filed.write(data)


def run_download_and_cut(  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches
    url: str,
    start_timestamp: str,
    end_timestamp: str,
    outname: str,
    log: bool = LOG,
    verbose: bool = False,
) -> None:
    """Runs a series of commands that downloads and cuts the given url to output filename."""
    outname = os.path.abspath(outname)
    os.makedirs(outname, exist_ok=True)
    try:
        if log:
            outlog = os.path.join(outname, "run.log")
            with open(outlog, encoding="utf-8", mode="w") as filed:
                filed.write("")

        video_path_tmpl = r"full_video.%(ext)s"
        yt_dlp_cmd: str = f'yt-dlp --no-check-certificate --force-overwrites --output "{video_path_tmpl}" {url}'  # pylint: disable=line-too-long
        if log:
            _append_file(outlog, f"Running: {yt_dlp_cmd}\nin {outname}")
        returncode, stdout, stderr = _exec(yt_dlp_cmd, verbose=verbose, cwd=outname)
        if log:
            _append_file(
                outlog,
                f"END ->> {yt_dlp_cmd} returned {returncode}\n\n {stdout+stderr}\n",
            )
        # Search through the output of the yt-dlp command to for the
        # file name.
        fullvideo = _find_video_file_from_stdout(stdout + stderr)
        if fullvideo is None or not os.path.exists(fullvideo):
            # try and find new video
            files = [
                os.path.join(outname, file)
                for file in os.listdir(outname)
                if (file.endswith(".mp4") or file.endswith(".webm"))
                and os.path.isfile(os.path.join(outname, file))
            ]
            if files:
                fullvideo = files[0]
            else:
                raise OSError(
                    f"Could not find a video in \n"
                    "###################\n"
                    f"{stdout}"
                    "\n###################\n"
                    f"with command '{yt_dlp_cmd}'\n"
                    f"RETURNED: {returncode}\n"
                )
        outfile = f"{outname}.mp4"
        ffmpeg_cmd = (
            f'static_ffmpeg -y -i "{fullvideo}"'  # accepts any prompts with y
            # start timestamp (seconds or h:mm:ss:ff)
            f" -ss {start_timestamp}"
            # length timestamp (seconds or h:mm:ss:ff)
            f" -to {end_timestamp}"
            f" {outfile}"
        )
        outfile_abs = os.path.join(outname, outfile)
        if os.path.exists(outfile_abs):
            if log:
                _append_file(outlog, f"Deleting previous file: {outfile_abs}\n")
            os.remove(outfile_abs)
        if log:
            _append_file(outlog, f"Running: {ffmpeg_cmd}\nin {outname}")
        returncode, stdout, stderr = _exec(ffmpeg_cmd, verbose=verbose, cwd=outname)
        if log:
            _append_file(
                outlog,
                f"END ->> {ffmpeg_cmd} returned {returncode}\n\n{stdout+stderr}\n",
            )
        if returncode != 0:
            raise OSError(
                f'Error running "{ffmpeg_cmd}".'
                "\n###################\n"
                f"STDOUT:\n{stdout}\n"
                "\n###################\n"
                f"STDERR:\n{stderr}\n"
                "\n###################\n"
                f'with command "{yt_dlp_cmd}"\n'
            )
    finally:
        if not KEEP:
            shutil.rmtree(outname, ignore_errors=True)


def _finish_then_print_completion(future):
    try:
        future.result()
        print(f'Finished job "{future.name}" with "{future.url}"')
    except BaseException as berr:  # pylint: disable=broad-except
        print(
            f'ERROR fetching clip from "{future.url}" because of error:\n' f"{berr}\n"
        )


def unit_test_brighteon():
    """Unit test for brighteon."""
    run_download_and_cut(
        "https://www.brighteon.com/f596cc8b-4b52-4152-92cb-39dadc552833",
        "10:47",
        "11:07",
        "health_ranger_report",
    )


def unit_test_bitchute():
    """Unit test for bitchute."""
    run_download_and_cut(
        "https://www.bitchute.com/video/pDCS8i20enIq",
        "08:08",
        "08:28",
        "sarah_westhall",
    )


def _epilog() -> str:
    return (
        "Example:\n"
        "  ytclip --url https://www.youtube.com/watch?v=CLXt3yh2g0s --start_timestamp 00:32 --end_timestamp 00:58 --outname myoutputfile\n"  # pylint: disable=line-too-long
        "Any missing arguments will be prompted.\n"
    )


def _run_concurrent() -> None:
    # Interactive mode.
    futures = []
    executor = ThreadPoolExecutor(max_workers=8)
    try:
        while True:
            print("Add new video:")
            url = input("  url: ")
            if url != "":
                start_timestamp = input("  start_timestamp: ")
                end_timestamp = input("  end_timestamp: ")
                output_name = input("  output_name (autosaved as mp4): ")

                def task():
                    return run_download_and_cut(
                        url=url,
                        start_timestamp=start_timestamp,
                        end_timestamp=end_timestamp,
                        outname=output_name,
                    )

                f = executor.submit(task)  # pylint: disable=invalid-name
                setattr(f, "url", url)
                setattr(f, "name", output_name)
                futures.append(f)
                print(f"\nStarting {url} in background.\n")
            # Have any futures completed?
            finished_futures = [
                f for f in futures if f.done()  # pylint: disable=invalid-name
            ]
            futures = [f for f in futures if f not in finished_futures]
            for f in finished_futures:  # pylint: disable=invalid-name
                _finish_then_print_completion(f)
            out_str = f"There are {len(futures)} jobs outstanding:\n"
            if len(futures):
                for f in futures:  # pylint: disable=invalid-name
                    out_str += f"\n  {f.name}"  # type: ignore
                out_str += "\n"
            out_str += "\n"
            print(out_str)

    except KeyboardInterrupt:
        print("\n\n")

    unfinished_futures = [f for f in futures if not f.done()]
    if unfinished_futures:
        print(f"Waiting for {len(unfinished_futures)} commands to finish")
        for i, f in enumerate(unfinished_futures):  # pylint: disable=invalid-name
            sys.stdout.write(f"  Waiting for {f.url} to finish...\n")  # type: ignore
            while not f.done():
                time.sleep(0.1)
            _finish_then_print_completion(f)
            sys.stdout.write(f"  ... done, {len(unfinished_futures)-i} left\n")
    print("All commands completed.")


def run_cmd() -> int:  # pylint: disable=too-many-branches,too-many-statements
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
    parser.add_argument("--start_timestamp", help="start timestamp of the clip")
    parser.add_argument("--end_timestamp", help="end timestamp of the clip")
    parser.add_argument("--outname", help="output name of the file (auto saved as mp4)")
    parser.add_argument("--keep", action="store_true", help="keeps intermediate files")
    args = parser.parse_args()
    if args.version:
        print(f"{VERSION}")
        return 0
    global LOG  # pylint: disable=global-statement
    global KEEP  # pylint: disable=global-statement
    if args.no_log:
        LOG = False
    if args.keep:
        KEEP = True

    if not args.concurrent:
        url = args.url or input("url: ")
        start_timestamp = args.start_timestamp or input("start_timestamp: ")
        end_timestamp = args.end_timestamp or input("end_timestamp: ")
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
        )
        if os.path.exists(outname):
            return 0
        return 1
    _run_concurrent()
    return 0


# Download tests take too long and YouTube has a habbit of deleting users
# so this test is run manually.
def unit_test_rap_video():
    """Weird title requires special handling for intermediate file name."""
    run_download_and_cut(
        url="https://www.youtube.com/watch?v=CLXt3yh2g0s",
        start_timestamp="00:32",
        end_timestamp="00:34",
        outname="myoutputfile",
    )


def main():
    """Just defaults to run_cmd."""
    run_cmd()


if __name__ == "__main__":
    # unit_test_brighteon()
    # unit_test_stdout_parse()
    # unit_test_bitchute()
    # unit_test_rap_video()
    main()
