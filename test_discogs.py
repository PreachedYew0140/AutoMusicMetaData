from my_discogs_client import DiscogsAPI

def test_search():
    api = DiscogsAPI()
    release = api.search_release("A Tribe Called Quest", "The Low End Theory")
    if not release:
        print("No release found")
        return
    print(f"Found release: {release.title} ({release.year})")

    tracklist = api.get_tracklist(release)
    for track in tracklist:
        print(track)

if __name__ == "__main__":
    test_search()