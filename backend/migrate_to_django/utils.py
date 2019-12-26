from pytz import timezone

ber_timezone = timezone('Europe/Berlin')
utc_timezone = timezone('UTC')


def non_naive_datetime_ber(input_datetime):
    """
    Used for datetimes
    """
    return ber_timezone.localize(input_datetime)


def non_naive_datetime_utc(input_datetime):
    """
    Used for unix timestamps
    """
    return utc_timezone.localize(input_datetime)
