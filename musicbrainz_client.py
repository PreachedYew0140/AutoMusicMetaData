import musicbrainzngs
import json

musicbrainzngs.set_useragent("AutoMusicMetaData", "1.0", "https://github.com/PreachedYew0140/AutoMusicMetaData")

class MusicBrainzClient:
    def search_release(self, artist, album):
        print(f"[MusicBrainzClient] Searching MusicBrainz for artist='{artist}', album='{album}'")
        result = musicbrainzngs.search_releases(artist=artist, release=album, limit=10)
        print("[MusicBrainzClient] search_release response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        releases = result.get('release-list', [])
        # Filter releases to those with exact album title match (case-insensitive, trimmed)
        album_clean = album.strip().lower()
        filtered = [r for r in releases if r.get('title', '').strip().lower() == album_clean]
        print(f"[MusicBrainzClient] Found {len(filtered)} releases with exact album title match.")
        if filtered:
            print(f"[MusicBrainzClient] First matched release title: {filtered[0].get('title', 'N/A')}, id: {filtered[0].get('id', 'N/A')}")
        else:
            print("[MusicBrainzClient] No exact album title matches found; using all results.")
        return filtered if filtered else releases

    def get_release_info(self, release_id):
        print(f"[MusicBrainzClient] Fetching release info for release_id={release_id}")
        result = musicbrainzngs.get_release_by_id(release_id, includes=["artists", "labels", "recordings", "release-groups", "media"])
        print(f"[MusicBrainzClient] get_release_info response for release_id={release_id}:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return result
