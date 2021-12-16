def recursive_equals(entry, remaining_attribute, value, id):
    result = []
    if len(remaining_attribute) == 1:
        if isinstance(entry[remaining_attribute[0]], list) or isinstance(entry[remaining_attribute[0]], dict):
            raise Exception(f'Tried to assert equality on a list/obj for {remaining_attribute[0]}')
        if entry[remaining_attribute[0]].lower() == value:
            return set([id])
        else:
            print(entry[remaining_attribute[0]] + " not equal to " + value)
            return set([])
    
    # otherwise we need to dive deeper
    try:
        to_explore = entry[remaining_attribute[0]]
    except KeyError as k:
        raise Exception(f'Tried to access an object that does not exist: {remaining_attribute}')

    if isinstance(to_explore, list):
        for item in to_explore:
            print(item)
            result.extend(recursive_equals(item, remaining_attribute[1:], value, id))
    else:
        result.extend(recursive_equals(to_explore, remaining_attribute[1:], value, id))
    
    return set(result)

def recursive_greater_than_equal_to(entry, remaining_attribute, value, id):
    result = []
    if len(remaining_attribute) == 1:
        if isinstance(entry[remaining_attribute[0]], list) or isinstance(entry[remaining_attribute[0]], dict):
            raise Exception(f'Tried to perform comparison on a list/obj for {remaining_attribute[0]}')
        if entry[remaining_attribute[0]] >= value:
            return set([id])
        else:
            return set([])
    
    # otherwise we need to dive deeper
    try:
        to_explore = entry[remaining_attribute[0]]
    except KeyError as k:
        raise Exception(f'Tried to access an object that does not exist: {remaining_attribute}')

    if isinstance(to_explore, list):
        for item in to_explore:
            result.extend(recursive_greater_than_equal_to(item, remaining_attribute[1:], value, id))
    else:
        result.extend(recursive_greater_than_equal_to(to_explore, remaining_attribute[1:], value, id))
    
    return set(result)



def recursive_less_than_equal_to(entry, remaining_attribute, value, id):
    result = []
    if len(remaining_attribute) == 1:
        if isinstance(entry[remaining_attribute[0]], list) or isinstance(entry[remaining_attribute[0]], dict):
            raise Exception(f'Tried to perform comparison on a list/obj for {remaining_attribute[0]}')
        if entry[remaining_attribute[0]] <= value:
            return set([id])
        else:
            return set([])
    
    # otherwise we need to dive deeper
    try:
        to_explore = entry[remaining_attribute[0]]
    except KeyError as k:
        raise Exception(f'Tried to access an object that does not exist: {remaining_attribute}')

    if isinstance(to_explore, list):
        for item in to_explore:
            result.extend(recursive_less_than_equal_to(item, remaining_attribute[1:], value, id))
    else:
        result.extend(recursive_less_than_equal_to(to_explore, remaining_attribute[1:], value, id))
    
    return set(result)

def recursive_contains(entry, remaining_attribute, value, id):
    result = []
    if len(remaining_attribute) == 1:
        if not isinstance(entry[remaining_attribute[0]], list) and not isinstance(entry[remaining_attribute[0]], str):
            raise Exception(f'Tried to perform contains on a non-list/non-string, {remaining_attribute[0]}, did you mean EQUALS?')
        if value in entry[remaining_attribute[0]]:
            return set([id])
        else:
            return set([])
    
    # otherwise we need to dive deeper
    try:
        to_explore = entry[remaining_attribute[0]]
    except KeyError as k:
        raise Exception(f'Tried to access an object that does not exist: {remaining_attribute}')

    if isinstance(to_explore, list):
        for item in to_explore:
            result.extend(recursive_contains(item, remaining_attribute[1:], value, id))
    else:
        result.extend(recursive_contains(to_explore, remaining_attribute[1:], value, id))
    
    return set(result)