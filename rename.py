# this script removes the \ufeff from the video names
from pathlib import Path

# Quick rename script
videos_dir = Path("categorized_videos")
for video_file in videos_dir.glob("**/*.mp4"):
    if '\ufeff' in video_file.name:
        new_name = video_file.name.replace('\ufeff', '')
        new_path = video_file.parent / new_name
        print(f"Renaming: {video_file.name} -> {new_name}")
        video_file.rename(new_path)

print("Done!")