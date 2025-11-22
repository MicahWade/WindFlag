from datetime import datetime, UTC

def make_datetime_timezone_aware(dt: datetime) -> datetime:
    """
    Ensures a datetime object is timezone-aware (UTC).
    If the datetime object is naive, it's assumed to be in UTC and localized.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt
