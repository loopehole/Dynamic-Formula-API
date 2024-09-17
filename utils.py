import re

def parse_currency(value):
    """Remove currency symbols and commas from the value."""
    value = re.sub(r'[^\d.]', '', value)
    return float(value)

def parse_percentage(value):
    """Remove percentage symbol and convert to decimal."""
    value = re.sub(r'%', '', value)
    return float(value) / 100
