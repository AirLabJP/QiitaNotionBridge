from utils import (
    format_datetime,
    parse_iso_datetime,
    get_jst_now,
    get_date_range,
    truncate_text,
)
from datetime import datetime, timedelta


def test_format_datetime():
    dt = datetime(2024, 5, 6)
    assert format_datetime(dt) == "2024-05-06"


def test_parse_iso_datetime():
    iso = "2024-05-06T12:34:56+09:00"
    dt = parse_iso_datetime(iso)
    assert dt.year == 2024 and dt.month == 5 and dt.day == 6


def test_get_jst_now():
    now = get_jst_now()
    assert now.tzinfo is not None


def test_get_date_range():
    start, end = get_date_range(3)
    assert (end - start).days == 3


def test_truncate_text():
    assert truncate_text("abcde", 3) == "abc..."
    assert truncate_text("abc", 3) == "abc"
    assert truncate_text("", 3) == ""
