import musicbrainzngs

musicbrainzngs.set_useragent("AutoMusicMetaData", "1.0", "https://github.com/PreachedYew0140/AutoMusicMetaData")

class MusicBrainzAPI:
    def search_release(self, artist, album):
        # Search for releases by artist and album
        result = musicbrainzngs.search_releases(artist=artist, release=album, limit=10)
        return result.get('release-list', [])

    def get_release_info(self, release_id):
        # Get full release info by MusicBrainz ID
        return musicbrainzngs.get_release_by_id(release_id, includes=["artists", "labels", "recordings", "release-groups", "media"])
