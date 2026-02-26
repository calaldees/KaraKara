#!/usr/bin/env python3

# %%

import json
from pathlib import Path

data = json.loads(Path("./tracks.json").read_text())

# %%
# Check for tracks with year<2000, but don't have the "retro" tag

for my_id, my_track in data.items():
    my_title = my_track["tags"]["title"][0]
    my_year = None
    if "year" in my_track["tags"]:
        try:
            my_year = int(my_track["tags"]["year"][0])
        except Exception:
            pass
    if my_year and my_year < 2000 and "retro" not in my_track["tags"]:
        print(my_id, my_title, my_year)

# %%
# Check for tracks with the "retro" tag, but don't have a year or date field

for my_id, my_track in data.items():
    my_title = my_track["tags"]["title"][0]
    my_year = None
    if "year" in my_track["tags"]:
        try:
            my_year = int(my_track["tags"]["year"][0])
        except Exception:
            pass
    has_retro = "retro" in my_track["tags"]
    if has_retro and not my_year and "date" not in my_track["tags"]:
        print(my_id, my_title)

# %%
# Check for tracks with the same subtitle file, which may indicate duplicates or instrumental versions.

sub2track: dict[str, str] = {}
for my_id, my_track in data.items():
    my_title = my_track["tags"]["title"][0]
    my_duration = my_track["duration"]
    try:
        my_subs = my_track["attachments"]["subtitle"][0]["path"]
        if my_subs in sub2track:
            print(sub2track[my_subs], my_id)
        else:
            sub2track[my_subs] = my_id
    except Exception:
        my_subs = None

# %%

for my_id, my_track in data.items():
    my_title = my_track["tags"]["title"][0]
    my_duration = my_track["duration"]
    if "Instrumental" in my_id:
        # id_without_instrumental = id.replace("_Instrumental", "")
        for ye_id, ye_track in data.items():
            ye_title = ye_track["tags"]["title"][0]
            ye_duration = ye_track["duration"]
            durdiff = abs(my_duration - ye_duration)
            if my_id == ye_id:
                continue
            if my_title == ye_title and durdiff < 1:
                print(my_id, "vs", ye_id, "durdiff=", durdiff)
            # ed = editdistance.eval(id_without_instrumental, other_id)
            # if ed < 5:
            #    print(id, "vs", other_id, "ed=", ed)
