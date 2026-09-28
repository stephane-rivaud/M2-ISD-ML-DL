# Datasets — ISD-1020

Register of the datasets used in the module. File identifiers,
code and docstrings stay in English (`fetch_*` / `load_*` in
[`fetch.py`](fetch.py)).

Loading from the repository root:

```python
from data.fetch import load_telco, load_ai4i, load_eco2mix, load_nab
```

In student notebooks, after a short urllib bootstrap that downloads
`data/fetch.py` (and `common/plots.py` when needed) if they are not already
next to the notebook, these functions are imported as above. If that
download fails, clone or download this repository so the `common/` and
`data/` folders sit next to the notebook.

## Where the bytes come from

`load_*` **always** applies the same order, in any environment
(local Jupyter, `nbconvert`, bare Colab):

1. **committed** copy `data/<name>.parquet` if the
   repository `data/` folder is visible;
2. cache `data/cache/<name>.parquet` (gitignored); if `data/cache/` is
   not writable, or if there is no repository, writes go to
   `/content/isd-1020-cache` (Colab) or `/tmp/isd-1020-cache` (outside Colab),
   unless overridden by `ISD1020_CACHE_DIR`;
3. parquet on the public course repository
   (`stephane-rivaud/M2-ISD-ML-DL`) at
   `https://raw.githubusercontent.com/stephane-rivaud/M2-ISD-ML-DL/main/data/<name>.parquet`
   — **on by default**; short timeout (connect 2 s, read 3 s); a
   failure (404, timeout) does not interrupt loading: the next step is
   tried, with no traceback;
4. download from the public **original source**, then write
   the cache.

Environment variables:

| Variable | Effect |
|---|---|
| `ISD1020_USE_COURSE_REPO=0` (`false` / `no` / `off`) | skip the course-repository step |
| `ISD1020_USE_COURSE_REPO=1` (`true` / `yes` / `on`) | force the course-repository step |
| `ISD1020_REPO=owner/fork` | other GitHub slug (does not re-enable a course-repository step explicitly cut) |
| `ISD1020_CACHE_DIR` | cache directory (unchanged) |
| `ISD1020_DATA_DIR` | `data/` directory (unchanged) |

Each step prints a line indicating the origin. The committed parquet
files are enough **without a network** as soon as one runs
**inside the repository**. On a bare Colab, the parquet is fetched from
this course repository (once, then cache).

`python data/fetch.py --all` regenerates the parquet files in `data/cache/`
from the sources (also used if a committed copy must be rebuilt).

## Table

| Dataset | Distribution | Domain | Source (exact URL) | Licence | Size | Day | File | Shape |
|---|---|---|---|---|---|---|---|---|
| Telco Customer Churn | committed | telecom | [IBM GitHub](https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv) (`Telco-Customer-Churn.csv`; same table as the Kaggle file `WA_Fn-UseC_-Telco-Customer-Churn.csv`, Kaggle not used) | IBM Cognos Analytics sample (free use for the samples); copy of the repository [IBM/telco-customer-churn-on-icp4d](https://github.com/IBM/telco-customer-churn-on-icp4d) under Apache-2.0 | 195 618 o parquet (commit) | D0 | `telco.parquet` | (7043, 21) |
| AI4I 2020 Predictive Maintenance | committed | industry / automotive | [UCI 601 zip](https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip) ([record](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset)) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (UCI page) | 182 314 o parquet (commit) | D1 | `ai4i.parquet` | (10000, 14) |
| RTE éCO2mix national consumption | committed | power grid | [ODRE](https://odre.opendatasoft.com/explore/dataset/eco2mix-national-cons-def/) `eco2mix-national-cons-def` CSV export `select=date,heure,consommation`; filter `startswith(date, "2023") OR startswith(date, "2024")` | **Licence Ouverte v2.0 (Etalab)** — ODRE metadata and [data.gouv.fr](https://www.data.gouv.fr/datasets/donnees-eco2mix-nationales-consolidees-et-definitives) (`lov2`). This is not ODbL. | 473 305 o parquet (commit) | D2 AM | `eco2mix.parquet` | (35088, 3) datetime index |
| Numenta Anomaly Benchmark `realKnownCause` | committed | ops / anomalies | [NAB](https://github.com/numenta/NAB) `data/realKnownCause/*.csv` + [`labels/combined_windows.json`](https://raw.githubusercontent.com/numenta/NAB/master/labels/combined_windows.json) | GitHub repository: **MIT** ([LICENSE.txt](https://raw.githubusercontent.com/numenta/NAB/master/LICENSE.txt), API `mit`, © 2014-2024 Numenta Inc.). | 1 002 040 o parquet (commit) | D2 PM | `nab.parquet` | (69561, 4) |

No dataset is *source-only*: every table can be rebuilt from the
source; the parquet copies are also versioned in `data/`.

## Import processing

- **Telco**: numeric `TotalCharges` (11 blanks → NaN).
- **AI4I**: `ai4i2020.csv` in the zip, columns unchanged.
- **éCO2mix**: **national France** perimeter (not IDF). Calendar years **2023–2024** (2 years in the 2022–2024 window). Columns `Date`, `Heure`, `Consommation (MW)`; 30 min datetime index; NaNs and 15 min steps dropped (the source has empty :15/:45 slots).
- **NAB**: the 7 `realKnownCause` series, `series` column; `is_anomaly` from the windows. D2 series: `machine_temperature_system_failure` (`NAB_FOCUS_SERIES`).

## Versioned files (`data/`, < 5 MB, permissive licences)

| File | Bytes |
|---|---|
| `data/telco.parquet` | 195 618 |
| `data/ai4i.parquet` | 182 314 |
| `data/eco2mix.parquet` | 473 305 |
| `data/nab.parquet` | 1 002 040 |

## Attributions

- Telco: IBM Cognos sample / [IBM/telco-customer-churn-on-icp4d](https://github.com/IBM/telco-customer-churn-on-icp4d) (Apache-2.0 for the code pattern).
- AI4I 2020: AI4I / UCI, CC BY 4.0.
- éCO2mix: RTE / ODRE, Licence Ouverte v2.0.
- NAB: Numenta Inc., MIT.
