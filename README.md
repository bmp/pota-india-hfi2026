# Parks on the Air (POTA) in India

Paper, presentation, scripts and data for *Parks on the Air (POTA) in India:
Current Operational Status and Pathways for Participation*, presented at
Hamfest India 2026, NITK Surathkal, Mangaluru (28–29 November 2026).

- Blog post with interactive charts: https://ham.bharathpalavalli.com/posts/20260709153650-pota_in_india/
- Presentation: https://ham.bharathpalavalli.com/posts/20261115205742-pota_in_india_by_the_numbers/presentation.html

## Layout

```
paper/
  submitted/       Paper as submitted for double-blind review (LaTeX, figures, PDF)
  camera-ready/    Final version, after acceptance
presentation/      Exported slides
scripts/           Analysis scripts and requirements.txt
data/
  2026-07-09-figure-data/   Plotly figure data behind the paper and post (July 2026)
  2026-11-15-snapshot/      Raw POTA API snapshot used for the November update
figures/           Static chart exports used in the presentation
```

## Scripts

Install the dependencies (tested with Python 3.15):

```sh
pip install -r scripts/requirements.txt
```

`01_*.py` to `09_*.py` are the scripts behind the blog post, one per chart or
table. They were run from Org Babel, so each one prints Org-mode/HTML output
to stdout. They query live APIs, so today's results will differ from the
paper.

| Script                      | Produces                                       |
|-----------------------------|------------------------------------------------|
| `01_parks_map.py`           | Map of POTA parks and the state-wise table     |
| `02_activation_timeline.py` | Cumulative activations over time               |
| `03_activation_tiers.py`    | Parks by activation tier                       |
| `04_lorenz_curve.py`        | Lorenz curve of activations by park rank       |
| `05_active_hf_census.py`    | Census of active VU HF operators               |
| `06_activator_profiles.py`  | Activator exploration vs. effort chart         |
| `07_license_class.py`       | General vs. Restricted grade comparison        |
| `08_activator_footprint.py` | Polar chart of activation distance and bearing |
| `09_hunters.py`             | Hunter landscape chart and world map           |

`08_activator_footprint.py` needs a HamQTH account:

```sh
export HAMQTH_USER=... HAMQTH_PASS=...
```

To take a fresh snapshot and compare it with July 2026:

```sh
python scripts/snapshot.py data/<date>-snapshot   # the directory must exist
python scripts/compare.py data/<date>-snapshot
```

`compare.py` recomputes the statistics with a 9 July 2026 cutoff, which
reproduces the paper's numbers, alongside the current totals.

## Data sources

POTA.app (https://api.pota.app), HamQTH, the Reverse Beacon Network,
PSKReporter, WSPRnet, ARRL LoTW, and the public CQ and ARRL contest log
archives. See the paper for access dates.

## Paper versions

- `paper/camera-ready/pota_india_hfi2026.pdf`: the corrected version. The changes from the submitted version are listed in `paper/camera-ready/CHANGES.md`.
- `paper/submitted/`: the version submitted for double-blind review, kept unchanged.

The hunter counts come from the POTA park leaderboards, which list at most
five hunters per park, so they are a lower bound.

## Licence

- Scripts: BSD 3-Clause (`LICENSE`)
- Figures and figure data: CC BY 4.0 (`LICENSE-CONTENT`)
- Raw POTA.app snapshot: subject to POTA.app's terms of use
- Paper: included for reference, under the copyright notice printed in it

## Contact

Bharath M. Palavalli, VU3GLJ (vu3glj@disroot.org)
