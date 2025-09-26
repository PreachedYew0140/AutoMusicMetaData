import os
from mutagen.flac import FLAC

def scan_folder(directory):
    """Return list of FLAC files paths in folder"""
    flac_files = []
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith('.flac'):
                flac_files.append(os.path.join(root, filename))
    return flac_files

def read_metadata(file_path):
    """Extract artist, album, and title from FLAC tags"""
    audio = FLAC(file_path)
    return {
        "artist": audio.get("artist", ["Unknown Artist"])[0],
        "album": audio.get("album", ["Unknown Album"])[0],
        "title": audio.get("title", ["Unknown Title"])[0]
    }

