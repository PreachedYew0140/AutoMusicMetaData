import sys 
from file_scanner import scan_folder, read_metadata
from my_discogs_client import DiscogsAPI
from tagger import rename_files

def main(folder):
    files = scan_folder(folder)
    if not files:
        print("No FLAC files found.")
        return

    # Use metadata from first file to identify release
    metadata = read_metadata(files[0])
    artist = metadata["artist"]
    album = metadata["album"]
    print(f"Extracted metadata from first FLAC file:")
    print(f"Artist: {artist}")
    print(f"Album: {album}")
    print(f"Searching Discogs for {artist} - {album}")

    api = DiscogsAPI()
    release = api.search_release(artist, album)

    if not release:
        print("No matching release found on Discogs.")
        return

    print(f"\nDiscogs release found:")
    print(f"Title: {getattr(release, 'title', 'N/A')}")
    print(f"Year: {getattr(release, 'year', 'N/A')}")
    print(f"URL: {getattr(release, 'url', 'N/A')}")

    tracklist = api.get_tracklist(release)
    print("\nDiscogs tracklist:")
    for pos, title in tracklist:
        print(f"{pos}: {title}")

    print("\nLocal files:") 
    files_sorted = sorted(files)
    for i, f in enumerate(files_sorted):
        print(f"{i+1}: {f}")
    print("\n")
    confirm = input("\nProceed with renaming files using this tracklist? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborted renaming.")
        return

    # Map files to tracklist (naive approach: order by filename sorted)
    file_map = {f: (i+1, tracklist[i][1]) for i, f in enumerate(files_sorted)}

    # Rename and update tags
    rename_files(file_map)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <folder_path>")
    else:
        main(sys.argv[1])