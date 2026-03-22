from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import pandas as pd
import yfinance as yf


TARGET_BARS = 260
FETCH_PERIOD = "3y"
OUTPUT_COLUMNS = ["symbol", "date", "open", "high", "low", "close", "adj_close", "volume"]


@dataclass(slots=True)
class DownloadResult:
    ticker: str
    output_path: Path
    row_count: int
    latest_date: str


def normalize_ticker(value: str) -> str:
    return re.sub(r"[^A-Z0-9._-]", "", str(value or "").strip().upper())


def build_output_path(directory: str | Path, ticker: str) -> Path:
    safe_ticker = normalize_ticker(ticker)
    return Path(directory).expanduser().resolve() / f"{safe_ticker}_daily_ohlcv.csv"


def download_ticker_csv(ticker: str, directory: str | Path, target_bars: int = TARGET_BARS) -> DownloadResult:
    normalized_ticker = normalize_ticker(ticker)
    if not normalized_ticker:
        raise ValueError("Ticker is required.")

    history = yf.Ticker(normalized_ticker).history(
        period=FETCH_PERIOD,
        interval="1d",
        auto_adjust=False,
        actions=False,
    )
    if history.empty:
        raise ValueError(f"No daily data returned for {normalized_ticker}.")

    frame = history.reset_index()
    date_column = next((column for column in frame.columns if str(column).lower().startswith("date")), None)
    if not date_column:
        raise ValueError("Downloaded data did not include a date column.")

    frame = frame.rename(
        columns={
            date_column: "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce", utc=True).dt.tz_convert(None).dt.date.astype(str)
    frame["symbol"] = normalized_ticker

    missing_columns = [column for column in OUTPUT_COLUMNS if column not in frame.columns]
    if missing_columns:
        joined = ", ".join(missing_columns)
        raise ValueError(f"Downloaded data is missing columns: {joined}")

    cleaned = frame[OUTPUT_COLUMNS].copy()
    cleaned = cleaned.dropna(subset=["date", "open", "high", "low", "close", "volume"])
    cleaned = cleaned.tail(target_bars)
    if len(cleaned) < 60:
        raise ValueError(f"Only {len(cleaned)} valid daily rows remain for {normalized_ticker}.")

    output_path = build_output_path(directory, normalized_ticker)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False)

    return DownloadResult(
        ticker=normalized_ticker,
        output_path=output_path,
        row_count=len(cleaned),
        latest_date=str(cleaned.iloc[-1]["date"]),
    )
