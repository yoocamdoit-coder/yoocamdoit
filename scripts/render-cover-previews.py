"""Extract the uninterrupted home preview sequences from the published films."""
from argparse import ArgumentParser
from pathlib import Path
import subprocess

# Start and exclusive end frames at 24 fps. None means play through the source end.
COVERS = {
    "commercial": ("run-alone", 417, None, "scale=960:540"),
    "personal": ("victor", 1851, 2180, "crop=iw*3/4:ih,scale=960:720"),
}

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    for name, (film, start, end, framing) in COVERS.items():
        length = [] if end is None else ["-frames:v", str(end - start)]
        subprocess.run([
            args.ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-threads", "2", "-ss", f"{start / 24:.6f}",
            "-i", str(args.media / f"{film}.mp4"), "-map", "0:v:0", "-an",
            "-filter_threads", "2", "-vf", f"fps=24,{framing},setsar=1",
            *length, "-c:v", "libx264", "-preset", "fast",
            "-crf", "24", "-maxrate", "1800k", "-bufsize", "3600k",
            "-threads", "2", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(args.media / f"{name}-preview.mp4"),
        ], check=True)

if __name__ == "__main__":
    main()
