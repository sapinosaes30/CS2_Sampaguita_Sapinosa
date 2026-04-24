import datetime

def required(value):
    return bool(value and str(value).strip())


def validate_date(date_text):
    try:
        datetime.date.fromisoformat(date_text)
        return True
    except (ValueError, TypeError):
        return False


def validate_time(time_text):
    try:
        datetime.time.fromisoformat(time_text)
        return True
    except (ValueError, TypeError):
        return False


def validate_priority(value):
    return value in ["Normal", "High", "Urgent"]
