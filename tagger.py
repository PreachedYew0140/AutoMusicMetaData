import os 
from mutagen.flac import FLAC

def rename_files(file_map):
    """
    file_map = { file_path: (track_number, track_title) }
    """
    for file_path, (track_number, track_title) in file_map.items():
        audio = FLAC(file_path)
        audio["tracknumber"] = str(track_number)
        audio["title"] = track_title
        audio.save()

    #{track_number:02d}
        folder = os.path.dirname(file_path)
        new_filename = f"{track_number:02d} - {track_title}.flac"
        new_path = os.path.join(folder, new_filename)
        os.rename(file_path, new_path)
        print(f"Renamed: {file_path} -> {new_path}")