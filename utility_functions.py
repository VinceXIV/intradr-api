def snake_case(str_):
    return str_.lower().replace(" ", "_")

def recursive_round(value, decimal_places):
    try:
        iter(value)
        return [recursive_round(val, decimal_places) for val in value]
    except:
        return round(float(value), decimal_places)
