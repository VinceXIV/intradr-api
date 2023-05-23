def snake_case(str_):
    return str_.lower().replace(" ", "_")

def recursive_round(value, decimal_places):
    try:
        iter(value)
        return [recursive_round(val, decimal_places) for val in value]
    except:
        try:
            return round(float(value), decimal_places)
        except:
            raise ValueError(
                "Value received was {value}, which is invalid. Possible reasons include; (1) Using function that don't exist as in a typo".format(value=value))
