from collections.abc import Sequence

from pm3.lib.track import Track


def view(tracks: Sequence[Track]) -> None:
    """
    Print out a list of Tracks, marking whether or not each Target (ie, each
    file in the "processsed" directory) exists
    """
    GREEN = "\033[92m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    OK = GREEN + "✔" + ENDC
    FAIL = RED + "✘" + ENDC

    for track in tracks:
        print(track.id)
        for t in track.targets:
            if t.path.exists():
                stats = f"{OK} ({int(t.path.stat().st_size / 1024):,} KB)"
            else:
                stats = FAIL
            print(f"  - {t} {stats}")
