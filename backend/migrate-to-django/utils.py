from pytz import timezone

bp_timezone = timezone('Europe/Budapest')
utc_timezone = timezone('UTC')


def non_naive_datetime_bp(input_datetime):
    """
    Used for datetimes
    """
    return bp_timezone.localize(input_datetime)


def non_naive_datetime_utc(input_datetime):
    """
    Used for unix timestamps
    """
    return utc_timezone.localize(input_datetime)
