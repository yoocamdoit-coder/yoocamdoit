"""Cut silent thumbnail loops from the six published portfolio films."""
from argparse import ArgumentParser
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

# Source time in seconds and shot length in frames at 24 fps.
MONTAGES = {
    "commercial": [
        ("run-alone", 19.25, 28),
        ("rum-summer", 90.65, 25),
        ("hui-switch", 5.52, 24),
        ("run-alone", 9.45, 23),
        ("rum-summer", 53.95, 29),
        ("hui-switch", 91.72, 28),
        ("rum-summer", 181.65, 27),
        ("run-alone", 25.95, 35),
    ],
    "personal": [
        ("victor", 52.20, 32),
        ("howfar", 157.00, 28),
        ("gone-and-again", 197.30, 29),
        ("victor", 29.75, 21),
        ("howfar", 104.55, 22),
        ("gone-and-again", 137.85, 28),
        ("howfar", 174.55, 28),
        ("gone-and-again", 217.00, 24),
        ("victor", 74.80, 31),
    ],
}

def render(ffmpeg, sources, output, name, shots):
    with TemporaryDirectory() as directory:
        montage = Path(directory)
        segments = []
        for index, (film, start, frames) in enumerate(shots):
            segment = montage / f"{index:02d}.mp4"
            # Victor has baked-in pillarboxes. Crop those out before reframing.
            crop = "crop=iw*3/4:ih," if film == "victor" else ""
            filters = crop + (
                "fps=24,scale=960:540:force_original_aspect_ratio=increase:"
                "force_divisible_by=2,crop=960:540,setsar=1"
            )
            subprocess.run([
                ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
                "-threads", "2", "-ss", str(start), "-i", str(sources / f"{film}.mp4"),
                "-map", "0:v:0", "-an", "-filter_threads", "2", "-vf", filters,
                "-frames:v", str(frames), "-c:v", "libx264", "-preset", "fast",
                "-crf", "23", "-maxrate", "1700k", "-bufsize", "3400k",
                "-threads", "2", "-pix_fmt", "yuv420p", str(segment),
            ], check=True)
            segments.append(f"file '{segment.name}'\n")
        listing = montage / "concat.txt"
        listing.write_text("".join(segments), encoding="ascii")
        subprocess.run([
            ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin", "-y",
            "-f", "concat", "-i", str(listing), "-c", "copy",
            "-movflags", "+faststart", str(output / f"{name}-teaser.mp4"),
        ], check=True)

def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("sources", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, shots in MONTAGES.items():
        render(args.ffmpeg, args.sources, args.output, name, shots)

if __name__ == "__main__":
    main()
