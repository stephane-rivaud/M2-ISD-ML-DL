# Datasets — ISD-1020

Register of the datasets used in the module. File identifiers,
code and docstrings stay in English (`fetch_*` / `load_*` in
[`fetch.py`](fetch.py)).

Loading from the repository root:

```python
from data.fetch import load_telco
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
3. GitHub release `data-v1` (`stephane-rivaud/M2-ISD-ML-DL`) —
   leftover fallback, **on by default**; short timeout
   (connect 2 s, read 3 s); a failure (404, timeout) does not interrupt
   loading: the next step is tried, with no traceback;
4. download from the public **original source**, then write
   the cache.

Environment variables:

| Variable | Effect |
|---|---|
| `ISD1020_USE_GITHUB_RELEASE=0` (`false` / `no` / `off`) | skip the release step |
| `ISD1020_USE_GITHUB_RELEASE=1` (`true` / `yes` / `on`) | force the release step |
| `ISD1020_REPO=owner/fork` | other GitHub slug (does not re-enable a release explicitly cut) |
| `ISD1020_CACHE_DIR` | cache directory (unchanged) |
| `ISD1020_DATA_DIR` | `data/` directory (unchanged) |

Each step prints a line indicating the origin. The committed parquet
files are enough **without a network** as soon as one runs
**inside the repository**. On a bare Colab, D0 downloads IBM's public CSV
(once, then cache).

`python data/fetch.py --all` regenerates the parquet files in `data/cache/`
from the sources (also used if a committed copy must be rebuilt).

## Table

| Dataset | Distribution | Domain | Source (exact URL) | Licence | Size | Day | File | Shape |
|---|---|---|---|---|---|---|---|---|
| Telco Customer Churn | committed | telecom | [IBM GitHub](https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv) (`Telco-Customer-Churn.csv`; same table as the Kaggle file `WA_Fn-UseC_-Telco-Customer-Churn.csv`, Kaggle not used) | IBM Cognos Analytics sample (free use for the samples); copy of the repository [IBM/telco-customer-churn-on-icp4d](https://github.com/IBM/telco-customer-churn-on-icp4d) under Apache-2.0 | 195 618 o parquet (commit) | D0 | `telco.parquet` | (7043, 21) |

No dataset is *source-only*: every table can be rebuilt from the
source; the parquet copies are also versioned in `data/`.

## Import processing

- **Telco**: numeric `TotalCharges` (11 blanks → NaN).

## Versioned files (`data/`, < 5 MB, permissive licences)

| File | Bytes |
|---|---|
| `data/telco.parquet` | 195 618 |

## Attributions

- Telco: IBM Cognos sample / [IBM/telco-customer-churn-on-icp4d](https://github.com/IBM/telco-customer-churn-on-icp4d) (Apache-2.0 for the code pattern).
