"""Render short, silent covers from the selected scenes of two portfolio films."""
from argparse import ArgumentParser
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

# Start time in seconds, then the number of frames to include at 24 fps.
COVERS = {
    "commercial": ("run-alone", 540, [(17.38, 134)]),
    "personal": ("victor", 720, [(77.54, 24), (80.20, 23), (87.68, 29), (90.34, 11)]),
}

def render(ffmpeg, media, key, film, height, cuts):
    with TemporaryDirectory() as directory:
        folder = Path(directory)
        segments = []
        # Victor's 4:3 frame is pillarboxed in its 16:9 source.
        crop = "crop=iw*3/4:ih," if film == "victor" else ""
        filters = f"{crop}fps=24,scale=960:{height},setsar=1"
        for index, (start, frames) in enumerate(cuts):
            clip = folder / f"{index:02d}.mp4"
            subprocess.run([
                ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                "-threads", "2", "-ss", str(start), "-i", str(media / f"{film}.mp4"),
                "-map", "0:v:0", "-an", "-filter_threads", "2", "-vf", filters,
                "-frames:v", str(frames), "-c:v", "libx264", "-preset", "fast",
                "-crf", "23", "-maxrate", "1600k", "-bufsize", "3200k",
                "-threads", "2", "-pix_fmt", "yuv420p", str(clip),
            ], check=True)
            segments.append(f"file '{clip.name}'\n")

        listing = folder / "concat.txt"
        listing.write_text("".join(segments), encoding="ascii")
        subprocess.run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-f", "concat", "-i", str(listing), "-c", "copy",
            "-movflags", "+faststart", str(media / f"{key}-preview.mp4"),
        ], check=True)

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    for key, (film, height, cuts) in COVERS.items():
        render(args.ffmpeg, args.media, key, film, height, cuts)

if __name__ == "__main__":
    main()
