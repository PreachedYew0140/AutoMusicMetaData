import os
from file_scanner import scan_folder, read_metadata
from tagger import rename_files
from my_discogs_client import DiscogsAPI
from mutagen.flac import FLAC
import json


class AlbumFolder:
    """
    Represents an album folder containing FLAC files and metadata.
    """
    def __init__(self, path, root_folder):
        self.path = path
        self.root_folder = root_folder
        self.flac_files = scan_folder(path)
        self.numbered_flac_files = self._filter_numbered_by_metadata(self.flac_files)
        self.metadata = read_metadata(self.numbered_flac_files[0]) if self.numbered_flac_files else {}
        # Try multiple fields for artist
        self.artist = (
            self.metadata.get("artist")
            or self.metadata.get("albumartist")
            or self.metadata.get("performer")
            or self.metadata.get("contributing_artist")
            or "Unknown Artist"
        )
        self.album = self.metadata.get("album", "Unknown Album")
        if self.numbered_flac_files:
            print(f"Metadata for {self.numbered_flac_files[0]}: {self.metadata}")
        else:
            print(f"No numbered FLAC files found in {self.path}.")

    def _filter_numbered_by_metadata(self, flac_files):
        """Return only FLAC files with a valid 'tracknumber' tag in metadata."""
        numbered = []
        for f in flac_files:
            try:
                audio = FLAC(f)
                tracknumber = audio.get("tracknumber", [None])[0]
                if tracknumber and str(tracknumber).isdigit():
                    numbered.append(f)
            except Exception:
                continue
        return numbered

    def is_already_processed(self):
        """Check if the album folder has already been processed."""
        parent = os.path.basename(os.path.dirname(self.path))
        return parent != os.path.basename(self.root_folder)

    def update_and_rename_tracks(self, tracklist, release_data):
        """
        Update FLAC metadata and rename each track to '{number} - {title}.flac'.
        Handles Discogs release_data format, including extraartists.
        Returns a list of new file paths.
        """
        new_paths = []
        for track, flac_file in zip(tracklist, self.flac_files):
            try:
                audio = FLAC(flac_file)
                # Update metadata
                audio['title'] = track.get('title', '')
                audio['tracknumber'] = track.get('number', '')
                # Discogs fields: use both artists and extraartists if available
                artist_names = []
                if 'artists' in release_data:
                    artist_names += [a['name'] for a in release_data['artists']]
                if 'extraartists' in release_data:
                    artist_names += [a['name'] for a in release_data['extraartists'] if 'name' in a]
                if artist_names:
                    audio['artist'] = ', '.join(artist_names)
                if 'year' in release_data:
                    audio['date'] = str(release_data['year'])
                if 'labels' in release_data:
                    label_names = [l['name'] for l in release_data['labels']]
                    audio['label'] = ', '.join(label_names)
                if 'genres' in release_data:
                    audio['genre'] = ', '.join(release_data['genres'])
                audio.save()
                # Rename file
                track_num = track.get('number', '').zfill(2)
                track_title = track.get('title', '').replace('/', '-').replace('\\', '-')
                new_filename = f"{track_num} - {track_title}.flac"
                new_path = os.path.join(os.path.dirname(flac_file), new_filename)
                os.rename(flac_file, new_path)
                new_paths.append(new_path)
                print(f"Renamed and updated metadata: {flac_file} -> {new_path}")
            except Exception as e:
                print(f"Error updating {flac_file}: {e}")
        return new_paths


class MusicLibraryOrganizer:
    """
    Orchestrates the scanning, matching, and organizing of music library folders using Discogs only.
    """
    def __init__(self, root_folder):
        self.root_folder = root_folder
        self.discogs_client = DiscogsAPI()

    def process(self, fix_inside=False):
        """
        Scan all album folders and organize them.
        If fix_inside is True, always fix file naming and metadata inside album folders.
        """
        for entry in os.scandir(self.root_folder):
            if entry.is_dir():
                album = AlbumFolder(entry.path, self.root_folder)
                if fix_inside or not album.is_already_processed():
                    self._process_album(album)

    def _process_album(self, album):
        """Find best Discogs release and organize album folder."""
        # First, try searching by artist and album
        discogs_release = self.discogs_client.search_release(album.artist, album.album)
        discogs_tracklist = None
        discogs_year = ''
        release_data = {}

        if discogs_release:
            discogs_tracklist = self.discogs_client.get_tracklist(discogs_release)
            discogs_year = getattr(discogs_release, 'year', '')
            release_data = getattr(discogs_release, 'data', {})
            if len(discogs_tracklist) == len(album.numbered_flac_files):
                tracklist = [{'number': pos, 'title': title} for pos, title in discogs_tracklist]
                year = str(discogs_year)
                self._confirm_and_organize_discogs(album, tracklist, year, discogs_release, release_data)
                return
            else:
                print("No suitable Discogs release found with matching track count for artist/album search.")

        # If not found, try searching by track title (using the first track as keyword)
        if album.numbered_flac_files:
            try:
                first_track_metadata = read_metadata(album.numbered_flac_files[0])
                track_title = first_track_metadata.get("title", "")
                if track_title:
                    print(f"Trying Discogs search by track: {track_title}")
                    discogs_release = self.discogs_client.search_release(album.artist, "", track=track_title)
                    if discogs_release:
                        discogs_tracklist = self.discogs_client.get_tracklist(discogs_release)
                        discogs_year = getattr(discogs_release, 'year', '')
                        release_data = getattr(discogs_release, 'data', {})
                        if len(discogs_tracklist) == len(album.numbered_flac_files):
                            tracklist = [{'number': pos, 'title': title} for pos, title in discogs_tracklist]
                            year = str(discogs_year)
                            self._confirm_and_organize_discogs(album, tracklist, year, discogs_release, release_data)
                            return
                        else:
                            print("No suitable Discogs release found with matching track count for track search.")
            except Exception as e:
                print(f"Error searching by track: {e}")

        print("No Discogs release found.")

    def _confirm_and_organize_discogs(self, album, tracklist, year, release, release_data):
        """Show release info, confirm, and organize files (Discogs only)."""
        print(f"\nBest Discogs search result:")
        print(json.dumps(getattr(release, 'data', release), indent=2, ensure_ascii=False))
        print(f"Year: {year}")
        print(f"Track count: Discogs={len(tracklist)}, Local={len(album.numbered_flac_files)}")
        confirm = input("\nProceed with tagging and organizing using this Discogs release? (y/n): ").strip().lower()
        if confirm == 'y':
            self._organize_files(album, tracklist, year, release_data)
        else:
            print("Aborted by user.")

    def _organize_files(self, album, tracklist, year, release_data):
        # Update metadata and rename files using AlbumFolder's method
        new_flac_files = album.update_and_rename_tracks(tracklist, release_data)
        year = self._validate_year(year)
        target_folder = self._create_target_folder(album.artist, album.album, year)
        moved_files = self._move_flac_files(new_flac_files, target_folder)
        self._move_other_files(album.path, target_folder)
        self._remove_original_folder(album.path)
        print(f"Organized files into: {target_folder}")

    def _validate_year(self, year):
        if year and year.isdigit() and len(year) == 4 and int(year) > 1900:
            return year
        return ''

    def _create_target_folder(self, artist, album, year):
        artist_folder = os.path.join(self.root_folder, artist)
        album_folder_name = f"{album} ({year})" if year else album
        target_folder = os.path.join(artist_folder, album_folder_name)
        os.makedirs(target_folder, exist_ok=True)
        return target_folder

    def _move_flac_files(self, flac_files, target_folder):
        moved_files = []
        for f in sorted(flac_files):
            new_path = os.path.join(target_folder, os.path.basename(f))
            os.rename(f, new_path)
            moved_files.append(new_path)
        return moved_files

    def _move_other_files(self, album_path, target_folder):
        for item in os.listdir(album_path):
            item_path = os.path.join(album_path, item)
            if not os.path.isfile(item_path) or not item_path.lower().endswith('.flac'):
                target_path = os.path.join(target_folder, item)
                if os.path.exists(target_path):
                    print(f"File already exists, skipping: {target_path}")
                    continue
                os.rename(item_path, target_path)

    def _remove_original_folder(self, album_path):
        try:
            os.rmdir(album_path)
        except Exception as e:
            print(f"Could not remove folder {album_path}: {e}")
