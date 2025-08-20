import discogs_client
from config import DISCOGS_USER_TOKEN

class DiscogsAPI:
    def __init__(self):
        self.client = discogs_client.Client('MusicTagger/0.1', user_token=DISCOGS_USER_TOKEN)

    def search_release(self, artist, album):
        """
        Search for a release using Discogs database search with accurate parameters.
        Safely access artist and album info from search results.
        """
        results = self.client.search(
            artist=artist,
            release_title=album,
            type='release'
        )
        filtered = []
        for r in results:
            # Safely get artist and title from search result data
            try:
                r_data = getattr(r, 'data', {})
                r_title = r_data.get('title', '').lower()
                r_artists = [a.lower() for a in r_data.get('artist', '').split(',')]
                if artist.lower() in r_artists and album.lower() == r_title:
                    filtered.append(r)
            except Exception:
                continue
        return filtered[0] if filtered else (results[0] if results else None)
    
    def get_tracklist(self, release):
        """Return ordered tracklist from a release."""
        return [(track.position, track.title) for track in release.tracklist] if release else []