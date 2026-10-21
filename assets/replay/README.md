# Replay with example data and no market connection

Learner entry: [frame-00.html](frame-00.html).

Open the file locally. Read the page. Record a raw response. Then open the link with the next label.

Each page contains only prices and events available at its cutoff.
Dates are labels for synthetic observations. They are not historical market records.
The replay does not use a network, login, script, analytics, or local storage.

The teacher source `teacher-case.json` contains the full future sequence and teacher observations.
The regeneration script also contains the full sequence.
Each next link shows a different observation. These steps give the instruction sequence. They do not prevent file access.

Before the raw response for this case at this cutoff, do not read the teacher source.
Do not give the teacher source or regeneration script as an observation packet to the learner model at this cutoff.

Do the procedure again from the repository root:

```powershell
python -B skills/ashare-market-learning/scripts/build_assets.py
```

From a directory, you can also use this command with an absolute script path.

SVG files are the primary source. PNG files are optional.

All fee and share-increment examples are assumptions for lessons. They are not trading rules at this time.

OHLC touches do not show the sequence of fills. They do not show execution availability or realized profit.
