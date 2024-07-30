"""
    Downloads and clips videos from youtube, rumble, bitchute (using yt-dlp) and clips
    the video using ffmpeg.
"""

import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple


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


def _clean_yt_url(url: str) -> str:
    """Cleans the url to be used with yt-dlp."""
    if "youtu.be" in url or "youtube.com" in url:
        # Remove the timestamp
        if "?t=" in url:
            url = url.split("?t=")[0]
    return url


def run_download_and_cut(  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
    url: str,
    start_timestamp: str,
    end_timestamp: str,
    outname: str,
    log: bool = True,
    verbose: bool = False,
    keep=False,
) -> None:
    """Runs a series of commands that downloads and cuts the given url to output filename."""
    url = _clean_yt_url(url)
    if not start_timestamp:
        assert (
            not end_timestamp
        ), "end_timestamp is required if start_timestamp is given"
    if not start_timestamp:
        assert (
            not end_timestamp
        ), "end_timestamp is must be None if start_timestamp is not None"
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
        is_drm_protected = "This video is drm protected" in (stdout + stderr)
        if is_drm_protected:
            raise OSError(
                "###################\n"
                f"{stdout}\n"
                f"{stderr}\n"
                "\n###################\n"
                f"with command '{yt_dlp_cmd}'\n"
                f"RETURNED: {returncode}\n"
                f"\n\nDRM protected video found at {url} and can't be downloaded.\n"
            )
        fullvideo = _find_video_file_from_stdout(stdout + stderr)
        if fullvideo is None or not os.path.exists(fullvideo):
            # try and find new video
            _append_file(
                outlog,
                f"ERROR: Could not find video file in {outname}\n",
            )

            files = [os.path.join(outname, file) for file in os.listdir(outname)]
            # Filter out non-video files
            files = [
                file
                for file in files
                if (
                    file.endswith(".mp4")
                    or file.endswith(".webm")
                    or file.endswith(".mkv")
                )
            ]

            # sort files such that webm is first, followed by mkv and then all the rest
            def rank_file(file: str):
                if file.endswith(".webm"):
                    return 0
                if file.endswith(".mkv"):
                    return 1
                return 2

            files.sort(key=rank_file)
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
        if os.path.exists(outfile):
            if log:
                _append_file(outlog, f"Deleting previous file: {outfile}\n")
            os.remove(outfile)
        if start_timestamp is None:
            _append_file(outlog, f"Copying {fullvideo} to {outfile}\n")
            shutil.copy(fullvideo, outfile)
            return
        relpath = os.path.relpath(fullvideo, outname)
        ffmpeg_cmd = f'static_ffmpeg -y -i "{relpath}"'  # accepts any prompts with y
        if start_timestamp:
            ffmpeg_cmd += f" -ss {start_timestamp}"
        if end_timestamp:
            ffmpeg_cmd += f" -to {end_timestamp}"
        ffmpeg_cmd += f' "{outfile}"'
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
        if not keep:
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


def run_concurrent() -> None:
    # Interactive mode.
    """Runs interactive concurrent mode."""
    futures = []
    executor = ThreadPoolExecutor(max_workers=8)
    try:
        while True:
            print("Add new video:")
            url = input("  url: ")
            if url != "":
                start_timestamp = input("  start_timestamp: ").strip()
                end_timestamp = input("  end_timestamp: ").strip()
                output_name = input("  output_name (autosaved as mp4): ").strip()

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


if __name__ == "__main__":
    run_download_and_cut(
        url="https://www.youtube.com/watch?v=oG25KSvFEq0",
        start_timestamp="",
        end_timestamp="",
        outname="myoutputfile",
    )
    # unit_test_brighteon()
    # unit_test_stdout_parse()
    # unit_test_bitchute()
    # unit_test_rap_video()
