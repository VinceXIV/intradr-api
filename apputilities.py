def process_data_dict(dict_):
    '''
    Receives data in the form {0: <variable_name>: <variable_value>, 1: <variable_name>: <variable_value>}
    and transforms it to {period: [0, 1], values: [3, 1]}. Also stringifies floats. Note the switch. that's
    because 1 represent the nearest
    '''
    result = {}
    for period in dict_:
        p = len(dict_) - period
        for variable in dict_[period]:
            value = dict_[period][variable]

            if(variable not in result):
                result[variable] = []

            result[variable].append((p, str(value)))

    return result

