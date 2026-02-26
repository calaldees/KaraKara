#!/usr/bin/env python3

"""
For each file given as argument, if the "date" field is missing, try to find it
using online APIs based on the "category" and "from" metadata fields, and append it
to the file.
"""

import sys
from pathlib import Path

import requests

# === API URLs ===
TVMAZE_SEARCH = "https://api.tvmaze.com/search/shows?q={}"
RAWG_SEARCH = "https://api.rawg.io/api/games?key=33874787ed84400d8abeffc13eb3b1dd"
MUSICBRAINZ_SEARCH = "https://musicbrainz.org/ws/2/recording/"


# === Utility functions ===
def parse_metadata(text):
    data = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip().lower()] = v.strip()
    return data


def has_date(text):
    return any(line.lower().startswith("date:") for line in text.splitlines())


def append_date(path, date, id=None):
    text = path.read_text(encoding="utf-8")
    sep = "" if text.endswith("\n") else "\n"

    text = text + f"{sep}date:{date}\n"
    if id:
        text += f"id:{id}\n"
    path.write_text(text, encoding="utf-8")


# === ANIME HANDLER ===
def search_anime(query):
    r = requests.get(TVMAZE_SEARCH.format(query), timeout=10)
    r.raise_for_status()
    return r.json()


def score_show(show, is_anime):
    score = 0
    if is_anime:
        network = show.get("network")
        country = network.get("country", {}).get("code") if network else None
        if country == "JP":
            score += 10
        if "anime" in (show.get("genres") or []):
            score += 5
    if show.get("premiered"):
        score += 1
    return score


def choose_show(results, is_anime):
    if not results:
        print("No matches found.")
        return None
    ranked = sorted(
        results, key=lambda r: score_show(r["show"], is_anime), reverse=True
    )
    for i, item in enumerate(ranked, 1):
        show = item["show"]
        name = show["name"]
        premiered = show.get("premiered") or "unknown"
        network = show.get("network")
        country = network["country"]["name"] if network else "N/A"
        print(f"{i}) {name} ({country}) – premiered {premiered}")
    print("s) skip")
    choice = input("Select a show: ").strip().lower()
    if choice == "s":
        return None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(ranked):
            return ranked[idx]["show"]
    print("Invalid selection.")
    return None


def handle_anime(meta, path):
    title = meta.get("title")
    series = meta.get("from")
    is_anime = meta.get("category") == "anime"
    print(f"Searching for: {series} ({path.name})")
    if is_anime:
        print("Anime detected 🎌")
    results = search_anime(series)
    show = choose_show(results, is_anime)
    if show and show.get("premiered"):
        append_date(path, show["premiered"])
        print(f"→ Appended date:{show['premiered']}")
    else:
        print("→ Skipped.")


# === GAME HANDLER ===
def search_games(query):
    params = {"search": query, "page_size": 10}
    r = requests.get(RAWG_SEARCH, params=params, timeout=10)
    r.raise_for_status()
    return r.json().get("results", [])


def choose_game(results):
    for i, g in enumerate(results, 1):
        print(f"{i}) {g['name']} – released {g.get('released', 'unknown')}")
    print("s) skip")
    choice = input("Select a game: ").strip().lower()
    if choice == "s":
        return None
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(results):
            return results[idx]
    print("Invalid selection.")
    return None


def handle_game(meta, path):
    game_name = meta.get("from").split(":")[-1]
    print(f"\nSearching for game: {game_name} ({path.name})")
    results = search_games(game_name)
    game = choose_game(results)
    if game and game.get("released"):
        # import pprint ; pprint.pprint(game)
        append_date(path, game["released"], id="rawg:" + str(game["id"]))
        print(f"→ Appended date:{game['released']}")
    else:
        print("→ Skipped.")


# === MUSIC HANDLER ===
def search_recordings(title, artist):
    query = f'recording:"{title}" AND artist:"{artist}"'
    params = {"query": query, "fmt": "json", "limit": 5}
    headers = {"User-Agent": "metadata-date-finder/1.0"}
    r = requests.get(MUSICBRAINZ_SEARCH, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json().get("recordings", [])


def get_release_candidates(recording):
    dates = []
    for rel in recording.get("releases", []):
        date = rel.get("date")
        title = rel.get("title")
        if date:
            dates.append((date, title))
    return dates


def choose_music_date(recordings):
    candidates = []
    for rec in recordings:
        for date, title in get_release_candidates(rec):
            candidates.append((date, rec["title"], title))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0])
    for i, (date, song, release) in enumerate(candidates, 1):
        print(f"{i}) {song} – {release} ({date})")
    print("s) skip")
    choice = input("Select a release: ").strip().lower()
    if choice.isdigit():
        return candidates[int(choice) - 1][0]
    return None


def handle_music(meta, path):
    title = meta.get("title")
    artist = meta.get("artist")
    print(f"Searching for recording: {title} – {artist}")
    recordings = search_recordings(title, artist)
    date = choose_music_date(recordings)
    if date:
        append_date(path, date)
        print(f"→ Appended date:{date}")
    else:
        print("→ Skipped.")


# === FILE PROCESSING ===
def process_file(path):
    text = path.read_text(encoding="utf-8")
    if has_date(text):
        # print(f"{path.name}: already has date, skipping.")
        return
    meta = parse_metadata(text)
    category = meta.get("category")
    if category == "anime":
        handle_anime(meta, path)
    elif category == "game":
        handle_game(meta, path)
    elif category in ("jpop", "kpop", "vocaloid"):
        handle_music(meta, path)
    else:
        print(f"{path.name}: unsupported category '{category}', skipping.")


# === MAIN ===
def main():
    if len(sys.argv) < 2:
        print("Usage: python add_dates.py <file1> [file2 ...]")
        sys.exit(1)
    for arg in sys.argv[1:]:
        path = Path(arg)
        if path.is_file():
            # print(f"\nProcessing {path.name}...")
            try:
                process_file(path)
            except Exception as e:
                pass
        else:
            print(f"{arg} is not a file.")


if __name__ == "__main__":
    main()
