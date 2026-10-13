"""Tiền xử lý S&P 500 và gán các cú sốc đã được nghiên cứu, không tải dữ liệu."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

EVENT_COLUMNS = ["date", "event", "description", "source_url", "source_url_2"]
OUTPUT_COLUMNS = ["date", "price", "Y", "Y_lag1", "D", "event"]
EXPECTED_EVENTS = 5
MIN_SESSION_GAP = 5
OUTLIER_LOG_THRESHOLD = 0.05  # Cờ sàng lọc, không phải tiêu chí loại quan sát.
ASSIGNMENT_RULE = "Giữ ngày có trong CSV; ngày không giao dịch gán phiên kế tiếp trong CSV."


class DataValidationError(ValueError):
    """Dữ liệu chưa đáp ứng điều kiện để tính lợi suất hoặc ước lượng mô hình."""


def parse_number(values: pd.Series) -> pd.Series:
    """Chuyển số Investing.com có dấu phẩy phân cách hàng nghìn."""
    text = values.astype("string").str.strip().str.replace(",", "", regex=False)
    return pd.to_numeric(text, errors="coerce").astype(float)


def parse_volume(values: pd.Series) -> pd.Series:
    """K = nghìn, M = triệu; rỗng/không parse được vẫn là missing, không điền 0."""
    text = values.astype("string").str.strip().str.upper().str.replace(",", "", regex=False)
    suffix = text.str.extract(r"([KM])$", expand=False)
    multiplier = suffix.map({"K": 1_000.0, "M": 1_000_000.0}).fillna(1.0)
    numeric = pd.to_numeric(text.str.replace(r"[KM]$", "", regex=True), errors="coerce")
    return (numeric * multiplier).astype(float)


def load_market(path: Path | str) -> tuple[pd.DataFrame, dict]:
    """Đọc, kiểm tra và tính Y/độ trễ; không ghi tệp, trả kèm báo cáo."""
    raw = pd.read_csv(path, dtype="string", encoding="utf-8-sig")
    raw.columns = raw.columns.str.strip()
    missing_columns = {"Date", "Price"} - set(raw.columns)
    if missing_columns:
        raise DataValidationError(f"Thiếu cột bắt buộc: {sorted(missing_columns)}")

    raw_missing = raw.isna() | raw.apply(lambda s: s.str.strip().eq(""))
    report = {
        "so_dong_goc": int(len(raw)),
        "missing_du_lieu_goc": {k: int(v) for k, v in raw_missing.sum().items()},
        "ban_ghi_trung_hoan_toan": int(raw.duplicated().sum()),
    }
    raw = raw.drop_duplicates().copy()
    cleaned = pd.DataFrame(index=raw.index)
    cleaned["date"] = pd.to_datetime(raw["Date"].str.strip(), format="%m/%d/%Y", errors="coerce")
    for source, target in [("Price", "price"), ("Open", "open"), ("High", "high"), ("Low", "low")]:
        cleaned[target] = parse_number(raw[source]) if source in raw else np.nan
    cleaned["volume"] = parse_volume(raw["Vol."]) if "Vol." in raw else np.nan
    cleaned["change_pct"] = (
        parse_number(raw["Change %"].str.replace("%", "", regex=False))
        if "Change %" in raw else np.nan
    )
    invalid_dates = cleaned["date"].isna()
    invalid_prices = ~np.isfinite(cleaned["price"]) | cleaned["price"].le(0)
    if invalid_dates.any() or invalid_prices.any():
        raise DataValidationError(
            f"Ngày thiếu/sai MM/DD/YYYY: {int(invalid_dates.sum())}; "
            f"giá thiếu/không hữu hạn/không dương: {int(invalid_prices.sum())}. "
            "Không nội suy hoặc tính lợi suất qua bản ghi bị loại."
        )

    duplicate_dates = cleaned[cleaned.duplicated("date", keep=False)]
    if not duplicate_dates.empty:
        fields = ["price", "open", "high", "low", "volume", "change_pct"]
        conflicts = duplicate_dates.groupby("date")[fields].nunique(dropna=False).gt(1).any(axis=1)
        if conflicts.any():
            bad_dates = conflicts[conflicts].index.strftime("%Y-%m-%d").tolist()
            raise DataValidationError(f"Ngày trùng có giá hoặc thông tin mâu thuẫn: {bad_dates}")
    report["ngay_trung_sau_parse"] = int(cleaned.duplicated("date").sum())
    cleaned = cleaned.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    cleaned["Y"] = np.log(cleaned["price"] / cleaned["price"].shift(1))
    cleaned["Y_lag1"] = cleaned["Y"].shift(1)

    ohlc = cleaned[["price", "open", "high", "low"]].notna().all(axis=1)
    invalid_ohlc = ohlc & (
        cleaned["low"].gt(cleaned["high"])
        | cleaned["price"].lt(cleaned["low"])
        | cleaned["price"].gt(cleaned["high"])
        | cleaned["open"].lt(cleaned["low"])
        | cleaned["open"].gt(cleaned["high"])
        | cleaned[["open", "high", "low"]].le(0).any(axis=1)
    )
    large_moves = cleaned["Y"].abs().gt(OUTLIER_LOG_THRESHOLD)
    report.update({
        "so_dong_sau_lam_sach": int(len(cleaned)),
        "ngay_dau": cleaned["date"].min().strftime("%Y-%m-%d"),
        "ngay_cuoi": cleaned["date"].max().strftime("%Y-%m-%d"),
        "missing_sau_parse": {k: int(v) for k, v in cleaned.isna().sum().items()},
        "so_ngay_cuoi_tuan_trong_csv": int(cleaned["date"].dt.dayofweek.ge(5).sum()),
        "so_bat_nhat_ohlc": int(invalid_ohlc.sum()),
        "ngay_bat_nhat_ohlc": cleaned.loc[invalid_ohlc, "date"].dt.strftime("%Y-%m-%d").tolist(),
        "nguong_sang_loc_abs_Y": OUTLIER_LOG_THRESHOLD,
        "bien_dong_lon_giu_nguyen": [
            {"date": r.date.strftime("%Y-%m-%d"), "Y": float(r.Y)}
            for r in cleaned.loc[large_moves, ["date", "Y"]].itertuples(index=False)
        ],
        "quy_tac": "Không nội suy giá; giữ missing volume; giữ biến động lớn, báo cáo cờ OHLC.",
    })
    return cleaned, report


def assign_events(market: pd.DataFrame, events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Gán đúng năm sự kiện lên lịch quan sát; từ chối mốc ngoài mẫu hoặc quá gần."""
    missing = set(EVENT_COLUMNS) - set(events.columns)
    if missing:
        raise DataValidationError(f"events.csv thiếu cột: {sorted(missing)}")
    if len(events) != EXPECTED_EVENTS:
        raise DataValidationError(f"Cần đúng {EXPECTED_EVENTS} sự kiện; nhận được {len(events)}.")
    events = events[EVENT_COLUMNS].copy()
    for column in EVENT_COLUMNS:
        if events[column].isna().any() or events[column].astype("string").str.strip().eq("").any():
            raise DataValidationError(f"Sự kiện thiếu thông tin ở cột {column}.")
    for column in ["source_url", "source_url_2"]:
        if not events[column].str.match(r"^https?://[^\s]+$").all():
            raise DataValidationError(f"URL không hợp lệ trong {column}.")
    if events["source_url"].eq(events["source_url_2"]).any():
        raise DataValidationError("Hai URL của một sự kiện phải khác nhau; tính độc lập đã được nghiên cứu.")
    events["date"] = pd.to_datetime(events["date"], format="%Y-%m-%d", errors="coerce")
    if events["date"].isna().any() or events["date"].duplicated().any():
        raise DataValidationError("Ngày sự kiện không hợp lệ hoặc bị trùng.")

    market = market.copy().sort_values("date").reset_index(drop=True)
    sessions = pd.DatetimeIndex(market["date"])
    if sessions.has_duplicates or sessions.empty:
        raise DataValidationError("Lịch quan sát rỗng hoặc còn ngày trùng.")
    if events["date"].lt(pd.Timestamp("2023-01-01")).any() or events["date"].gt(sessions[-1]).any():
        raise DataValidationError("Sự kiện ngoài khoảng 01/01/2023 đến ngày cuối CSV.")
    if events["date"].lt(sessions[0]).any():
        raise DataValidationError("Sự kiện trước ngày đầu CSV; không đủ giá để khảo sát phản ứng.")
    positions = sessions.searchsorted(pd.DatetimeIndex(events["date"]), side="left")
    if len(np.unique(positions)) != EXPECTED_EVENTS:
        raise DataValidationError("Nhiều sự kiện cùng gán một phiên; không có đủ năm ngày D=1.")
    gaps = np.diff(np.sort(positions))
    if (gaps < MIN_SESSION_GAP).any():
        raise DataValidationError(f"Các sự kiện cần cách nhau ít nhất {MIN_SESSION_GAP} phiên.")
    if market.loc[positions, ["Y", "Y_lag1"]].isna().any().any():
        raise DataValidationError("Có sự kiện thiếu Y/độ trễ; cần đủ lịch sử giá trước sự kiện.")

    events["date_assigned"] = sessions.take(positions).to_numpy()
    events = events.sort_values("date").reset_index(drop=True)
    event_map = events.set_index("date_assigned")["event"]
    market["event"] = market["date"].map(event_map).fillna("")
    market["D"] = market["date"].isin(event_map.index).astype(int)
    if int(market["D"].sum()) != EXPECTED_EVENTS:
        raise DataValidationError("Kiểm tra D=1 thất bại.")
    return market[OUTPUT_COLUMNS], events


def preprocess(root: Path | str | None = None) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Chạy pipeline, in báo cáo, xuất processed.csv và ghi date_assigned vào events.csv."""
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    market, report = load_market(data_dir / "sp500.csv")
    events_raw = pd.read_csv(data_dir / "events.csv", dtype="string", encoding="utf-8-sig")
    processed, events = assign_events(market, events_raw)
    positions = pd.DatetimeIndex(market["date"]).get_indexer(events["date_assigned"])
    report["so_ngay_D_bang_1"] = int(processed["D"].sum())
    report["khoang_cach_phien_su_kien"] = np.diff(positions).astype(int).tolist()
    report["quy_tac_gan_ngay"] = ASSIGNMENT_RULE
    print("BÁO CÁO TIỀN XỬ LÝ")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    table = events[["date", "date_assigned", "event"]].merge(
        processed[["date", "Y"]].rename(columns={"date": "date_assigned"}), on="date_assigned"
    )
    print("BẢNG GÁN SỰ KIỆN VÀ LỢI SUẤT LOG TỪ CSV")
    print(table.to_string(index=False))
    # Chỉ ghi sau khi toàn bộ kiểm tra đầu vào đã thành công.
    processed.to_csv(data_dir / "processed.csv", index=False, date_format="%Y-%m-%d", encoding="utf-8-sig")
    events.to_csv(data_dir / "events.csv", index=False, date_format="%Y-%m-%d", encoding="utf-8-sig")
    return processed, events, report


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        preprocess(args.root)
    except (DataValidationError, FileNotFoundError) as error:
        parser.exit(1, f"Lỗi tiền xử lý: {error}\n")


if __name__ == "__main__":
    main()
