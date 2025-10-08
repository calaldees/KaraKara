import datetime

import dateparser
import pytimeparse2


def parse_timedelta(
    duration: int | float | str | None | datetime.timedelta,
) -> datetime.timedelta | None:
    """
    >>> parse_timedelta(None)
    >>> parse_timedelta('')
    >>> parse_timedelta(0)
    datetime.timedelta(0)
    >>> parse_timedelta(datetime.timedelta(seconds=1))
    datetime.timedelta(seconds=1)
    >>> parse_timedelta(2.0)
    datetime.timedelta(seconds=2)
    >>> parse_timedelta('3')
    datetime.timedelta(seconds=3)
    >>> parse_timedelta('4 seconds')
    datetime.timedelta(seconds=4)
    >>> parse_timedelta('PT1M30S')
    datetime.timedelta(seconds=90)
    >>> parse_timedelta('NOT REAL')
    Traceback (most recent call last):
    ValueError: ...
    >>> parse_timedelta(-1)
    Traceback (most recent call last):
    ValueError: ...
    >>> parse_timedelta('5 seconds ago')
    Traceback (most recent call last):
    ValueError: ...
    >>> parse_timedelta(60.25)
    datetime.timedelta(seconds=60, microseconds=250000)
    """
    if duration is None or duration == "":
        return None
    if isinstance(duration, datetime.timedelta):
        return duration
    seconds = duration
    if isinstance(duration, (int, float)):
        seconds = duration
    if isinstance(duration, str):
        # ISO durations (used by pydantic / msgspec, etc),
        # eg "PT1M30S", can be parsed by pytimeparse2 if
        # we strip "PT" from the front.
        if duration.startswith("PT"):
            duration = duration[2:]
        seconds = pytimeparse2.parse(duration)
    if not isinstance(seconds, (int, float)):
        raise ValueError(f"unable to parse seconds from {duration}")
    if seconds < 0:
        raise ValueError("must be positive")
    return datetime.timedelta(seconds=seconds)


def parse_datetime(
    value: str | int | float | None | datetime.datetime,
) -> datetime.datetime | None:
    """
    >>> parse_datetime(None)
    >>> parse_datetime('')
    >>> parse_datetime(0)
    datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    >>> parse_datetime('1973-11-29 21:33:09.123457')
    datetime.datetime(1973, 11, 29, 21, 33, 9, 123457, tzinfo=datetime.timezone.utc)
    >>> parse_datetime(datetime.datetime(1970, 1, 1, 0, 0))
    datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    >>> parse_datetime('2022-01-01T09:50:00.000000')
    datetime.datetime(2022, 1, 1, 9, 50, tzinfo=datetime.timezone.utc)
    >>> parse_datetime('1st January 2000')
    datetime.datetime(2000, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)
    >>> parse_datetime('tomorrow midnight')
    datetime.datetime(...)
    >>> parse_datetime('NOT REAL')
    Traceback (most recent call last):
    ValueError: ...
    """
    # dt = datetime.datetime.fromisoformat(isoformatString)
    if value is None or value == "":
        return None
    dt: datetime.datetime | None = None
    if isinstance(value, datetime.datetime):
        dt = value
    if isinstance(value, (int, float)):
        dt = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
    if isinstance(value, str):
        dt = dateparser.parse(value)
        if not dt:
            raise ValueError(f"unable to parse datetime {value}")
    if not dt:
        return None
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    # if dt < (datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=1)):
    #    raise ValueError(f'dates in the past are probably not what you want {dt}')
    return dt
