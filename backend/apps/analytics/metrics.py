"""Pure calculation helpers for analytics: no ORM queries here.

Business date ranges are interpreted in the active timezone (Asia/Dubai,
per settings.TIME_ZONE), independent of how Order.ordered_at is stored.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.utils import timezone as dj_timezone
from django.utils.dateparse import parse_date

TWO_PLACES = Decimal("0.01")
DEFAULT_DASHBOARD_DAYS = 30


class InvalidDateRangeError(ValueError):
    pass


class InvalidBranchError(ValueError):
    pass


def round_money(value) -> Decimal:
    if value is None:
        value = 0
    return Decimal(value).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def safe_divide(numerator, denominator) -> Decimal:
    numerator = Decimal(numerator or 0)
    denominator = Decimal(denominator or 0)
    if denominator == 0:
        return Decimal("0.00")
    return round_money(numerator / denominator)


def growth_percentage(current, previous) -> float:
    """((current - previous) / previous) * 100, safe against a zero previous value."""
    current = Decimal(current or 0)
    previous = Decimal(previous or 0)
    if previous == 0:
        return 0.0
    return float(round(((current - previous) / previous) * 100, 1))


@dataclass(frozen=True)
class DateRange:
    start_date: date
    end_date: date

    @property
    def days(self) -> int:
        return (self.end_date - self.start_date).days + 1

    def previous_period(self) -> "DateRange":
        """The immediately preceding period of the same length (e.g. 7 days -> prior 7 days)."""
        length = self.days
        prev_end = self.start_date - timedelta(days=1)
        prev_start = prev_end - timedelta(days=length - 1)
        return DateRange(start_date=prev_start, end_date=prev_end)


def datetime_bounds(date_range: DateRange):
    """Half-open [start, end) aware datetime range in the current business timezone."""
    tz = dj_timezone.get_current_timezone()
    start_dt = dj_timezone.make_aware(datetime.combine(date_range.start_date, time.min), tz)
    end_dt = dj_timezone.make_aware(
        datetime.combine(date_range.end_date + timedelta(days=1), time.min), tz
    )
    return start_dt, end_dt


def resolve_date_range(
    start_date_str, end_date_str, default_days: int = DEFAULT_DASHBOARD_DAYS
) -> DateRange:
    if not start_date_str and not end_date_str:
        end = dj_timezone.localdate()
        start = end - timedelta(days=default_days - 1)
        return DateRange(start_date=start, end_date=end)

    if not start_date_str or not end_date_str:
        raise InvalidDateRangeError("Both start_date and end_date must be provided together.")

    start = parse_date(start_date_str)
    end = parse_date(end_date_str)
    if start is None or end is None:
        raise InvalidDateRangeError("Dates must be in YYYY-MM-DD format.")
    if start > end:
        raise InvalidDateRangeError("start_date must not be after end_date.")

    return DateRange(start_date=start, end_date=end)
