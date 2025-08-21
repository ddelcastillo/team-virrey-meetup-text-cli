"""Date utility functions for Pokémon meetup events.

This module provides functions for calculating event dates, particularly
for finding the current or next Monday for Dynamax Monday events.
"""

from datetime import datetime, timedelta
from typing import Literal


def get_next_monday(*, from_date: datetime | None = None) -> datetime:
    """Get the date of the current or next Monday.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        DateTime object representing the current or next Monday.
    """
    if from_date is None:
        from_date = datetime.now()

    # Monday is weekday 0 in Python
    days_until_monday = (7 - from_date.weekday()) % 7

    # If today is Monday, return today; otherwise return next Monday
    if from_date.weekday() == 0:
        return from_date
    else:
        return from_date + timedelta(days=days_until_monday)


def format_spanish_date(*, date: datetime, format_type: Literal["full", "short"] = "full") -> str:
    """Format a date in Spanish.

    Args:
        date: DateTime object to format.
        format_type: Type of formatting - "full" or "short".

    Returns:
        Formatted date string in Spanish.
    """
    # Spanish month names
    spanish_months = {
        1: "enero",
        2: "febrero",
        3: "marzo",
        4: "abril",
        5: "mayo",
        6: "junio",
        7: "julio",
        8: "agosto",
        9: "septiembre",
        10: "octubre",
        11: "noviembre",
        12: "diciembre",
    }

    # Spanish day names
    spanish_days = {0: "lunes", 1: "martes", 2: "miércoles", 3: "jueves", 4: "viernes", 5: "sábado", 6: "domingo"}

    day_name = spanish_days[date.weekday()]
    month_name = spanish_months[date.month]

    if format_type == "full":
        return f"{day_name} {date.day} de {month_name}"
    else:  # short
        return f"{date.day} de {month_name}"


def get_dynamax_monday_date(*, from_date: datetime | None = None) -> str:
    """Get the formatted date for the next Dynamax Monday event.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        Formatted Spanish date string for the Dynamax Monday event.
    """
    monday_date = get_next_monday(from_date=from_date)
    return format_spanish_date(date=monday_date, format_type="full")


def get_current_week_info(*, from_date: datetime | None = None) -> dict[str, str | bool | int]:
    """Get information about the current week for event planning.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        Dictionary with week information including next Monday date.
    """
    if from_date is None:
        from_date = datetime.now()

    next_monday = get_next_monday(from_date=from_date)

    return {
        "next_monday_date": format_spanish_date(date=next_monday, format_type="full"),
        "next_monday_short": format_spanish_date(date=next_monday, format_type="short"),
        "is_today_monday": from_date.weekday() == 0,
        "days_until_monday": (next_monday - from_date).days,
        "current_date": format_spanish_date(date=from_date, format_type="full"),
    }


def get_next_tuesday(*, from_date: datetime | None = None) -> datetime:
    """Get the date of the current or next Tuesday.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        DateTime object representing the current or next Tuesday.
    """
    if from_date is None:
        from_date = datetime.now()

    # Tuesday is weekday 1 in Python
    days_until_tuesday = (1 - from_date.weekday()) % 7

    # If today is Tuesday, return today; otherwise return next Tuesday
    if from_date.weekday() == 1:
        return from_date
    else:
        return from_date + timedelta(days=days_until_tuesday)


def get_spotlight_tuesday_date(*, from_date: datetime | None = None) -> str:
    """Get the formatted date for the next Spotlight Hour Tuesday event.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        Formatted Spanish date string for the Spotlight Hour Tuesday event.
    """
    tuesday_date = get_next_tuesday(from_date=from_date)
    return format_spanish_date(date=tuesday_date, format_type="full")


def get_next_wednesday(*, from_date: datetime | None = None) -> datetime:
    """Get the date of the current or next Wednesday.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        DateTime object representing the current or next Wednesday.
    """
    if from_date is None:
        from_date = datetime.now()

    # Wednesday is weekday 2 in Python
    days_until_wednesday = (2 - from_date.weekday()) % 7

    # If today is Wednesday, return today; otherwise return next Wednesday
    if from_date.weekday() == 2:
        return from_date
    else:
        return from_date + timedelta(days=days_until_wednesday)


def get_legendary_wednesday_date(*, from_date: datetime | None = None) -> str:
    """Get the formatted date for the next Legendary Hour Wednesday event.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        Formatted Spanish date string for the Legendary Hour Wednesday event.
    """
    wednesday_date = get_next_wednesday(from_date=from_date)
    return format_spanish_date(date=wednesday_date, format_type="full")


def get_next_saturday(*, from_date: datetime | None = None) -> datetime:
    """Get the date of the current or next Saturday.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        DateTime object representing the current or next Saturday.
    """
    if from_date is None:
        from_date = datetime.now()

    # Saturday is weekday 5 in Python
    days_until_saturday = (5 - from_date.weekday()) % 7

    # If today is Saturday, return today; otherwise return next Saturday
    if from_date.weekday() == 5:
        return from_date
    else:
        return from_date + timedelta(days=days_until_saturday)


def get_next_sunday(*, from_date: datetime | None = None) -> datetime:
    """Get the date of the current or next Sunday.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        DateTime object representing the current or next Sunday.
    """
    if from_date is None:
        from_date = datetime.now()

    # Sunday is weekday 6 in Python
    days_until_sunday = (6 - from_date.weekday()) % 7

    # If today is Sunday, return today; otherwise return next Sunday
    if from_date.weekday() == 6:
        return from_date
    else:
        return from_date + timedelta(days=days_until_sunday)


def get_weekend_event_date(*, day_choice: int, from_date: datetime | None = None) -> str:
    """Get the formatted date for the next weekend event.

    Args:
        day_choice: 1 for Saturday, 2 for Sunday.
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        Formatted Spanish date string for the weekend event.
    """
    if day_choice == 1:
        event_date = get_next_saturday(from_date=from_date)
    elif day_choice == 2:
        event_date = get_next_sunday(from_date=from_date)
    else:
        raise ValueError("day_choice must be 1 (Saturday) or 2 (Sunday)")

    return format_spanish_date(date=event_date, format_type="full")


def get_max_battle_day_date(*, day_choice: int, from_date: datetime | None = None) -> str:
    """Get the formatted date for the next Max Battle Day event.

    Args:
        day_choice: 1 for Saturday, 2 for Sunday.
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        Formatted Spanish date string for the Max Battle Day event.
    """
    return get_weekend_event_date(day_choice=day_choice, from_date=from_date)


def get_raid_day_date(*, day_choice: int, from_date: datetime | None = None) -> str:
    """Get the formatted date for the next Raid Day event.

    Args:
        day_choice: 1 for Saturday, 2 for Sunday.
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        Formatted Spanish date string for the Raid Day event.
    """
    return get_weekend_event_date(day_choice=day_choice, from_date=from_date)


def get_next_thursday(*, from_date: datetime | None = None) -> datetime:
    """Get the date of the current or next Thursday.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        DateTime object representing the current or next Thursday.
    """
    if from_date is None:
        from_date = datetime.now()

    # Thursday is weekday 3 in Python
    days_until_thursday = (3 - from_date.weekday()) % 7

    # If today is Thursday, return today; otherwise return next Thursday
    if from_date.weekday() == 3:
        return from_date
    else:
        return from_date + timedelta(days=days_until_thursday)


def get_next_friday(*, from_date: datetime | None = None) -> datetime:
    """Get the date of the current or next Friday.

    Args:
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        DateTime object representing the current or next Friday.
    """
    if from_date is None:
        from_date = datetime.now()

    # Friday is weekday 4 in Python
    days_until_friday = (4 - from_date.weekday()) % 7

    # If today is Friday, return today; otherwise return next Friday
    if from_date.weekday() == 4:
        return from_date
    else:
        return from_date + timedelta(days=days_until_friday)


def get_next_day_of_week(*, weekday: int, from_date: datetime | None = None) -> datetime:
    """Get the date of the current or next specified day of the week.

    Args:
        weekday: Day of week (0=Monday, 1=Tuesday, ..., 6=Sunday).
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        DateTime object representing the current or next specified day.
    """
    if from_date is None:
        from_date = datetime.now()

    days_until_day = (weekday - from_date.weekday()) % 7

    # If today is the specified day, return today; otherwise return next occurrence
    if from_date.weekday() == weekday:
        return from_date
    else:
        return from_date + timedelta(days=days_until_day)


def get_legendary_hour_date(*, day_choice: int, from_date: datetime | None = None) -> str:
    """Get the formatted date for the next Legendary Hour event on the specified day.

    Args:
        day_choice: Day choice (1=Monday, 2=Tuesday, etc.).
        from_date: Date to calculate from. If None, uses current date.

    Returns:
        Formatted Spanish date string for the Legendary Hour event.
    """
    # Convert day_choice to 0-based weekday index
    weekday = day_choice - 1
    event_date = get_next_day_of_week(weekday=weekday, from_date=from_date)
    return format_spanish_date(date=event_date, format_type="full")
