def middle_value_dictionary(list_of_dicts):
    """
    Calculate the middle values of the keys 'x', 'y', 'width' and 'height' for a list of dictionaries
    :param list_of_dicts: list of dictionaries containing keys 'x', 'y', 'width' and 'height'
    :return: dictionary with keys 'x', 'y', 'width' and 'height' and average values
    """
    keys = ['x', 'y', 'width', 'height']
    middle_values = {}

    for key in keys:
        # convert to integer before calculation, as the input seems to be strings
        total = sum(int(dic[key]) for dic in list_of_dicts)
        avg = total / len(list_of_dicts)
        middle_values[key] = str(int(avg))  # convert back to string

    return middle_values

input_data = [{'x': '240', 'y': '80', 'width': '100', 'height': '80'}, {'x': '400', 'y': '80', 'width': '100', 'height': '80'}, {'x': '560', 'y': '80', 'width': '100', 'height': '80'}]
print(middle_value_dictionary(input_data))
