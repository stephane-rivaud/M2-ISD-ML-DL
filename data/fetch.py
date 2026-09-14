#!/usr/bin/env python3
"""Download, post-process and cache the ISD-1020 teaching datasets.

Each ``fetch_*`` function documents its exact source URL and post-processing.
Parquet caches are written to ``data/cache/<name>.parquet`` (gitignored)
when that directory is writable. If there is no repository (a bare Colab
VM) or ``data/cache`` is not writable, caches go to ``/content/isd-1020-cache``
(or ``/tmp/isd-1020-cache`` when ``/content`` is absent). Reads still look
in ``data/cache/`` first. Small, permissively licensed copies also live in
``data/<name>.parquet`` (committed); ``load_*`` prefers those.

``load_*`` always resolves, in every environment (local Jupyter, nbconvert,
a bare Colab VM): committed copy → local cache → GitHub release ``data-v1``
(when that tier is enabled) → original public source (then cache). The release
tier is **on by default** and is tried only for assets that exist on the
release (``eco2mix``, ``nab``, ``idfm``). A 404 or timeout does not raise: the
public URL is tried next. Release HTTP uses a short timeout (connect
2 s, read 3 s) so a missing release cannot stall a classroom. Disable with
``ISD1020_USE_GITHUB_RELEASE=0``; force on with ``=1``. ``ISD1020_REPO``
overrides the GitHub slug. Override the cache directory with
``ISD1020_CACHE_DIR`` and the data directory with ``ISD1020_DATA_DIR``.
Tag: ``data-v1``. Those files are committed in ``data/`` and remain
release assets as a fallback, plus ``idfm.LICENSE.txt`` (ODbL).
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import zipfile
from collections.abc import Callable
from pathlib import Path

import pandas as pd
import requests

_COLAB_CACHE_DIR = Path("/content/isd-1020-cache")
_LOCAL_FALLBACK_CACHE_DIR = Path("/tmp/isd-1020-cache")


def fallback_cache_dir() -> Path:
    """Writable cache when ``data/cache`` cannot be created or written."""
    content = Path("/content")
    if content.is_dir() and os.access(content, os.W_OK):
        return _COLAB_CACHE_DIR
    return _LOCAL_FALLBACK_CACHE_DIR


def _looks_like_data_dir(path: Path) -> bool:
    return path.is_dir() and (
        (path / "DATASETS.md").is_file() or (path / "telco.parquet").is_file()
    )


def resolve_data_dir() -> Path:
    """Locate ``data/`` when running from the repository; otherwise a writable fallback."""
    override = os.environ.get("ISD1020_DATA_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()

    file_name = globals().get("__file__")
    if file_name:
        here = Path(file_name)
        try:
            here = here.resolve()
        except OSError:
            here = Path(file_name)
        if here.is_file() and _looks_like_data_dir(here.parent):
            return here.parent

    for candidate in (Path.cwd(), *Path.cwd().parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "common").is_dir():
            data = candidate / "data"
            if data.is_dir():
                return data.resolve()
        data = candidate / "data"
        if _looks_like_data_dir(data):
            return data.resolve()
    return fallback_cache_dir()


def resolve_cache_dir(data_dir: Path) -> Path:
    """Prefer ``data/cache`` when writable; otherwise a session-local directory."""
    override = os.environ.get("ISD1020_CACHE_DIR", "").strip()
    if override:
        path = Path(override).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path.resolve()
    try:
        if data_dir.resolve() == fallback_cache_dir().resolve():
            data_dir.mkdir(parents=True, exist_ok=True)
            return data_dir.resolve()
    except OSError:
        pass
    preferred = data_dir / "cache"
    probe = preferred if preferred.is_dir() else data_dir
    if probe.is_dir() and os.access(probe, os.W_OK):
        return preferred
    return fallback_cache_dir()


DATA_DIR = resolve_data_dir()
CACHE_DIR = resolve_cache_dir(DATA_DIR)

DEFAULT_GITHUB_REPO_SLUG = "stephane-rivaud/M2-ISD-ML-DL"
RELEASE_TAG = "data-v1"


def github_repo_slug() -> str:
    return os.environ.get("ISD1020_REPO", DEFAULT_GITHUB_REPO_SLUG).strip() or (
        DEFAULT_GITHUB_REPO_SLUG
    )


_RELEASE_FLAG_OFF = frozenset({"0", "false", "no", "off"})
_RELEASE_FLAG_ON = frozenset({"1", "true", "yes", "on"})


def github_release_enabled() -> bool:
    """True unless ``ISD1020_USE_GITHUB_RELEASE`` is an explicit off value.

    Default is on. ``ISD1020_USE_GITHUB_RELEASE=0`` (or false/no/off) skips
    the release. ``=1`` (or true/yes/on) forces it. ``ISD1020_REPO`` only
    changes the slug; it does not override an explicit off.
    """
    flag = os.environ.get("ISD1020_USE_GITHUB_RELEASE", "").strip().lower()
    if flag in _RELEASE_FLAG_OFF:
        return False
    if flag in _RELEASE_FLAG_ON:
        return True
    return True


GITHUB_REPO_SLUG = DEFAULT_GITHUB_REPO_SLUG
IDFM_LICENSE_FILENAME = "idfm.LICENSE.txt"
RELEASE_ASSETS = (
    "eco2mix.parquet",
    "nab.parquet",
    "idfm.parquet",
    IDFM_LICENSE_FILENAME,
)

_USER_AGENT = "ISD-1020-course-pack/0.1 (Université Paris-Saclay teaching)"
# (connect, read). Connect is short so a dead host fails fast in a classroom.
_SOURCE_TIMEOUT: tuple[float, float] = (8.0, 45.0)
# Release tier: fail fast on 404 / hang (every student pays this when the
# release does not resolve). 2 s connect, 3 s read: a GitHub 404 returns in
# well under that; a hung handshake cannot stall the room more than 5 s.
_RELEASE_TIMEOUT: tuple[float, float] = (2.0, 3.0)
_EXPORT_TIMEOUT: tuple[float, float] = (8.0, 90.0)

TELCO_URL = (
    "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/"
    "master/data/Telco-Customer-Churn.csv"
)
AI4I_ZIP_URL = (
    "https://archive.ics.uci.edu/static/public/601/"
    "ai4i+2020+predictive+maintenance+dataset.zip"
)
AI4I_ZIP_MEMBER = "ai4i2020.csv"
BIKE_ZIP_URL = "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip"
BIKE_ZIP_MEMBER = "day.csv"

ECO2MIX_EXPORT_URL = (
    "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/"
    "eco2mix-national-cons-def/exports/csv"
)
# Local calendar years 2023–2024 (2 years of the 2022–2024 window). The source
# stores ``date`` as text, so filter with startswith rather than a date compare.
ECO2MIX_WHERE = 'startswith(date, "2023") OR startswith(date, "2024")'

NAB_SERIES_BASE = (
    "https://raw.githubusercontent.com/numenta/NAB/master/data/realKnownCause/"
)
NAB_LABELS_URL = (
    "https://raw.githubusercontent.com/numenta/NAB/master/labels/combined_windows.json"
)
# D2 PM uses this series; the parquet still contains every realKnownCause file.
NAB_FOCUS_SERIES = "machine_temperature_system_failure"
NAB_SERIES = (
    "ambient_temperature_system_failure",
    "cpu_utilization_asg_misconfiguration",
    "ec2_request_latency_system_failure",
    "machine_temperature_system_failure",
    "nyc_taxi",
    "rogue_agent_key_hold",
    "rogue_agent_key_updown",
)

IDFM_CATALOG = (
    "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/"
)
# Most recent published pair of daily rail-validation quarters (H2 2025).
IDFM_QUARTERS = (
    "validations-reseau-ferre-nombre-validations-par-jour-3eme-trimestre",
    "validations-reseau-ferre-nombre-validations-par-jour-4eme-trimestre",
)

COMMITTED_DATASETS = frozenset({"telco", "ai4i", "bike", "eco2mix", "nab", "idfm"})
REQUIRED_DATASETS = frozenset({"telco", "ai4i"})

_SESSION = requests.Session()
_SESSION.headers["User-Agent"] = _USER_AGENT


def _announce(name: str, message: str) -> None:
    print(f"{name}: {message}", flush=True)


def _release_asset_url(filename: str) -> str:
    return (
        f"https://github.com/{github_repo_slug()}/releases/download/"
        f"{RELEASE_TAG}/{filename}"
    )


def _get(
    url: str,
    *,
    params: dict[str, str] | None = None,
    timeout: float | tuple[float, float] = _SOURCE_TIMEOUT,
) -> bytes:
    response = _SESSION.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.content


def _existing_cache_path(name: str) -> Path | None:
    """Prefer a readable parquet in ``data/cache``, then the writable cache dir."""
    seen: set[Path] = set()
    for directory in (DATA_DIR / "cache", CACHE_DIR):
        path = directory / f"{name}.parquet"
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path
        if resolved in seen:
            continue
        seen.add(resolved)
        if path.is_file():
            return path
    return None


def _cache_path(name: str) -> Path:
    return CACHE_DIR / f"{name}.parquet"


def _committed_path(name: str) -> Path:
    return DATA_DIR / f"{name}.parquet"


def _ensure_writable_cache_dir() -> Path:
    global CACHE_DIR
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        return CACHE_DIR
    except OSError:
        fallback = fallback_cache_dir()
        if fallback.resolve() == Path(CACHE_DIR).resolve():
            raise
        fallback.mkdir(parents=True, exist_ok=True)
        CACHE_DIR = fallback
        return CACHE_DIR


def _write_cache(name: str, frame: pd.DataFrame) -> Path:
    directory = _ensure_writable_cache_dir()
    path = directory / f"{name}.parquet"
    frame.to_parquet(path)
    return path


def _read_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def _is_release_parquet(name: str) -> bool:
    return f"{name}.parquet" in RELEASE_ASSETS


def _load_release_asset(name: str) -> pd.DataFrame:
    filename = f"{name}.parquet"
    return _read_parquet(io.BytesIO(_get(_release_asset_url(filename), timeout=_RELEASE_TIMEOUT)))


def _source_load_error(name: str, source_exc: BaseException) -> RuntimeError:
    tried = ["copy shipped in data/", "local cache"]
    if github_release_enabled() and _is_release_parquet(name):
        tried.append("fast copy")
    tried.append("the original source")
    return RuntimeError(
        f"{name}: could not load the dataset. Tried: {', '.join(tried)}. "
        f"Check your network. "
        f"Last error: {type(source_exc).__name__}: {source_exc}"
    )


def _load(name: str, fetch: Callable[[], pd.DataFrame]) -> pd.DataFrame:
    """Return committed copy, then cache, then GitHub release, then source."""
    if name in COMMITTED_DATASETS and _looks_like_data_dir(DATA_DIR):
        committed = _committed_path(name)
        if committed.is_file():
            _announce(name, f"loaded from the course copy data/{name}.parquet")
            return _read_parquet(committed)
    cached = _existing_cache_path(name)
    if cached is not None:
        try:
            label = f"data/{cached.relative_to(DATA_DIR)}"
        except ValueError:
            label = str(cached)
        _announce(name, f"loaded from the local cache {label}")
        return _read_parquet(cached)
    if github_release_enabled() and _is_release_parquet(name):
        try:
            frame = _load_release_asset(name)
        except (requests.RequestException, ValueError, OSError):
            _announce(
                name,
                "fast copy unavailable, downloading from the original source",
            )
        else:
            _announce(name, "loaded from the fast copy")
            _write_cache(name, frame)
            return frame
    try:
        frame = fetch()
    except Exception as source_exc:  # noqa: BLE001 — wrap any source failure for students
        raise _source_load_error(name, source_exc) from None
    _announce(name, "downloaded from the original source")
    return frame


def _read_zip_csv(content: bytes, member: str) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(content)) as archive, archive.open(member) as handle:
        return pd.read_csv(handle)


def fetch_telco() -> pd.DataFrame:
    """IBM Telco Customer Churn (D0).

    URL: IBM public GitHub mirror of the Cognos sample CSV
    ``Telco-Customer-Churn.csv`` (same table as Kaggle
    ``WA_Fn-UseC_-Telco-Customer-Churn.csv``; Kaggle is not used, it needs auth).

    Post-processing: coerce ``TotalCharges`` to numeric (blanks → NaN).
    """
    frame = pd.read_csv(io.BytesIO(_get(TELCO_URL)))
    frame["TotalCharges"] = pd.to_numeric(frame["TotalCharges"], errors="coerce")
    _write_cache("telco", frame)
    return frame


def load_telco() -> pd.DataFrame:
    return _load("telco", fetch_telco)


def fetch_ai4i() -> pd.DataFrame:
    """AI4I 2020 Predictive Maintenance (D1), UCI dataset 601.

    URL: ``https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip``

    Post-processing: read ``ai4i2020.csv`` from the zip, no column drops.
    """
    frame = _read_zip_csv(_get(AI4I_ZIP_URL), AI4I_ZIP_MEMBER)
    _write_cache("ai4i", frame)
    return frame


def load_ai4i() -> pd.DataFrame:
    return _load("ai4i", fetch_ai4i)


def fetch_eco2mix() -> pd.DataFrame:
    """RTE éCO2mix national consumption, 30-min, calendar 2023–2024 (D2 AM).

    URL: ODRE Opendatasoft export of ``eco2mix-national-cons-def`` with
    ``select=date,heure,consommation`` and ``where`` restricted to dates whose
    ``date`` text starts with 2023 or 2024. Perimeter is **national (France)**,
    not Île-de-France: two years at 30 min is ~35 k rows.

    Post-processing: keep ``Date``, ``Heure``, ``Consommation (MW)``; parse a
    datetime index from Date+Heure; drop NaNs. The source has 15-min slots with
    empty consumption on :15/:45; dropping NaNs (and keeping minutes in
    {0, 30}) yields a 30-min series. Redistributed as release asset
    ``eco2mix.parquet`` (Licence Ouverte v2.0).
    """
    content = _get(
        ECO2MIX_EXPORT_URL,
        params={
            "select": "date,heure,consommation",
            "where": ECO2MIX_WHERE,
            "order_by": "date,heure",
            "delimiter": ",",
        },
        timeout=_EXPORT_TIMEOUT,
    )
    frame = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")
    frame = frame.rename(
        columns={
            "date": "Date",
            "heure": "Heure",
            "consommation": "Consommation (MW)",
        }
    )
    frame["Consommation (MW)"] = pd.to_numeric(frame["Consommation (MW)"], errors="coerce")
    frame["datetime"] = pd.to_datetime(
        frame["Date"].astype(str) + " " + frame["Heure"].astype(str),
        errors="coerce",
    )
    frame = frame.dropna(subset=["datetime", "Consommation (MW)"])
    frame = frame.set_index("datetime").sort_index()
    frame = frame[frame.index.minute.isin([0, 30])]
    frame = frame[["Date", "Heure", "Consommation (MW)"]]
    _write_cache("eco2mix", frame)
    return frame


def load_eco2mix() -> pd.DataFrame:
    return _load("eco2mix", fetch_eco2mix)


def _nab_anomaly_mask(timestamps: pd.Series, windows: list[list[str]]) -> pd.Series:
    flag = pd.Series(False, index=timestamps.index)
    for start, end in windows:
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        flag = flag | ((timestamps >= start_ts) & (timestamps <= end_ts))
    return flag


def fetch_nab() -> pd.DataFrame:
    """Numenta Anomaly Benchmark, ``realKnownCause`` (D2 PM).

    URLs:
    - series: ``https://raw.githubusercontent.com/numenta/NAB/master/data/realKnownCause/<name>.csv``
    - labels: ``https://raw.githubusercontent.com/numenta/NAB/master/labels/combined_windows.json``

    Post-processing: concatenate every ``realKnownCause`` CSV with a ``series``
    column; parse ``timestamp``; add ``is_anomaly`` from ``combined_windows.json``.
    The D2 notebook can filter ``series == "machine_temperature_system_failure"``.
    Redistributed as release asset ``nab.parquet`` (MIT).
    """
    labels = json.loads(_get(NAB_LABELS_URL))
    frames: list[pd.DataFrame] = []
    for series in NAB_SERIES:
        url = f"{NAB_SERIES_BASE}{series}.csv"
        piece = pd.read_csv(io.BytesIO(_get(url)))
        piece["timestamp"] = pd.to_datetime(piece["timestamp"])
        piece.insert(0, "series", series)
        key = f"realKnownCause/{series}.csv"
        piece["is_anomaly"] = _nab_anomaly_mask(piece["timestamp"], labels.get(key, []))
        frames.append(piece)
    frame = pd.concat(frames, ignore_index=True)
    _write_cache("nab", frame)
    return frame


def load_nab() -> pd.DataFrame:
    return _load("nab", fetch_nab)


def _idfm_quarter_via_groupby(dataset_id: str) -> pd.DataFrame:
    url = f"{IDFM_CATALOG}{dataset_id}/records"
    payload = json.loads(
        _get(
            url,
            params={
                "select": "jour,sum(nb_vald) as validations",
                "group_by": "jour",
                "limit": "100",
                "order_by": "jour",
            },
        )
    )
    results = payload.get("results") or []
    if not results:
        raise RuntimeError(f"empty group_by response for {dataset_id}")
    frame = pd.DataFrame(results)
    return frame


def _idfm_quarter_via_csv(dataset_id: str) -> pd.DataFrame:
    url = f"{IDFM_CATALOG}{dataset_id}/exports/csv"
    content = _get(
        url,
        params={"select": "jour,nb_vald", "delimiter": ","},
        timeout=_EXPORT_TIMEOUT,
    )
    frame = pd.read_csv(io.BytesIO(content), encoding="utf-8-sig")
    frame["nb_vald"] = pd.to_numeric(frame["nb_vald"], errors="coerce")
    frame = (
        frame.dropna(subset=["jour", "nb_vald"])
        .groupby("jour", as_index=False)["nb_vald"]
        .sum()
        .rename(columns={"nb_vald": "validations"})
    )
    return frame


def _idfm_quarter_daily(dataset_id: str) -> pd.DataFrame:
    try:
        frame = _idfm_quarter_via_groupby(dataset_id)
    except (requests.RequestException, RuntimeError, ValueError, KeyError):
        frame = _idfm_quarter_via_csv(dataset_id)
    frame["date"] = pd.to_datetime(
        pd.to_datetime(frame["jour"], utc=True).dt.strftime("%Y-%m-%d")
    )
    frame["validations"] = pd.to_numeric(frame["validations"], errors="coerce")
    frame = frame.dropna(subset=["date", "validations"])
    return frame[["date", "validations"]]


def fetch_idfm() -> pd.DataFrame:
    """IDFM daily Navigo validations on the rail network, H2 2025 (D3).

    URLs (Opendatasoft Explore API v2.1), recent quarter pair:

    - ``.../validations-reseau-ferre-nombre-validations-par-jour-3eme-trimestre``
    - ``.../validations-reseau-ferre-nombre-validations-par-jour-4eme-trimestre``

    Post-processing: sum ``nb_vald`` per ``jour`` (network total, all stops and
    ticket categories) so the D3 practical loads in seconds. Q3 stores
    ``nb_vald`` as text, so ``sum()`` via ODSQL fails; that quarter is aggregated
    from a two-column CSV export.

    Redistributed as its own release asset ``idfm.parquet`` (ODbL, French
    version) plus companion ``idfm.LICENSE.txt``. This file is a derived daily
    aggregate, not the raw extract.
    """
    pieces = [_idfm_quarter_daily(dataset_id) for dataset_id in IDFM_QUARTERS]
    frame = pd.concat(pieces, ignore_index=True)
    frame = frame.drop_duplicates(subset=["date"]).set_index("date").sort_index()
    frame["validations"] = frame["validations"].astype("int64")
    _write_cache("idfm", frame)
    return frame


def load_idfm() -> pd.DataFrame:
    return _load("idfm", fetch_idfm)


def fetch_bike() -> pd.DataFrame:
    """UCI Bike Sharing daily counts (D3 fallback), UCI dataset 275.

    URL: ``https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip``

    Post-processing: read ``day.csv`` (daily, matching the IDFM daily task);
    parse ``dteday`` as datetime.
    """
    frame = _read_zip_csv(_get(BIKE_ZIP_URL), BIKE_ZIP_MEMBER)
    frame["dteday"] = pd.to_datetime(frame["dteday"])
    _write_cache("bike", frame)
    return frame


def load_bike() -> pd.DataFrame:
    return _load("bike", fetch_bike)


FETCHERS: dict[str, Callable[[], pd.DataFrame]] = {
    "telco": fetch_telco,
    "ai4i": fetch_ai4i,
    "eco2mix": fetch_eco2mix,
    "nab": fetch_nab,
    "idfm": fetch_idfm,
    "bike": fetch_bike,
}


def fetch_all() -> int:
    """Fetch every dataset. A failure does not abort the others.

    Exit code is non-zero only if Telco or AI4I (required for D0/D1) failed.
    """
    _ensure_writable_cache_dir()
    failed_required = False
    for name, fetcher in FETCHERS.items():
        try:
            frame = fetcher()
            path = _cache_path(name)
            print(f"{name}: shape={frame.shape} cached={path}")
        except Exception as exc:  # noqa: BLE001 — CLI must survive any dataset error
            reason = " ".join(str(exc).split())
            print(f"{name}: FAILED {reason}")
            if name in REQUIRED_DATASETS:
                failed_required = True
    return 1 if failed_required else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch ISD-1020 datasets into data/cache/")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download every dataset; continue after individual failures.",
    )
    args = parser.parse_args(argv)
    if not args.all:
        parser.print_help()
        return 2
    return fetch_all()


if __name__ == "__main__":
    sys.exit(main())
