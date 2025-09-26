# --- Imports ---
import os
import sys
from file_scanner import scan_folder, read_metadata
from music_library_organizer import MusicLibraryOrganizer


# --- Helper Functions ---
def is_already_processed(album_folder, root_folder):
    """
    Returns True if the album folder is already inside the correct artist/album structure.
    """
    parent = os.path.basename(os.path.dirname(album_folder))
    return parent != os.path.basename(root_folder)

# --- Entry Point ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <root_music_folder>")
    else:
        organizer = MusicLibraryOrganizer(sys.argv[1])
        # Always process all album folders, even if already organized,
        # to ensure inside files are correctly named and tagged.
        organizer.process(fix_inside=True)