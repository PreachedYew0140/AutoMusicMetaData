import discogs_client
from config import DISCOGS_USER_TOKEN
import json

class DiscogsAPI:
    def __init__(self):
        self.client = discogs_client.Client('MusicTagger/0.1', user_token=DISCOGS_USER_TOKEN)

    def search_release(self, artist, album, track=None):
        """
        Search for a release using Discogs database search with artist, album, and optionally track.
        Logs the full JSON data for debugging.
        """
        search_kwargs = {
            "artist": artist,
            "release_title": album,
            "type": "release"
        }
        if track:
            search_kwargs["track"] = track
        results = self.client.search(**search_kwargs)
        releases = [r for r in results]
        print(f"[DiscogsAPI] Found {len(releases)} releases for artist='{artist}', album='{album}', track='{track}'")
        for r in releases:
            print(json.dumps(getattr(r, 'data', {}), indent=2, ensure_ascii=False))
        if releases:
            return releases[0]
        else:
            print("[DiscogsAPI] No releases found.")
            return None

    def get_tracklist(self, release):
        """Return ordered tracklist from a release."""
        if release:
            print(f"[DiscogsAPI] Tracklist for release '{release.title}':")
            for track in release.tracklist:
                print(f"{track.position}: {track.title}")
            return [(track.position, track.title) for track in release.tracklist]
        else:
            print("[DiscogsAPI] No release provided for tracklist.")
            return []