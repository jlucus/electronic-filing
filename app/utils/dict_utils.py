# dictionary helper functions
from app.utils.string_utils import is_int


def get_value_at_path(data: dict, path: list):
    """
    Retrieve the dictionary value at a key path.
    """
    sub_tree = data
    if not isinstance(path, list):
        return None
    last_index = len(path) - 1

    for i in range(last_index):
        sub_tree = sub_tree.get(path[i], {})

    last_path = path[last_index]
    if "[" in last_path and "]" in last_path:
        ii = last_path.replace("[", "").replace("]", "")
        if not is_int(ii):
            # raise KeyError
            print(f"KeyError")
            return None
        ii = int(ii)
        return sub_tree[ii]

    return sub_tree.get(path[last_index], None)


def map_key(
    source: dict,
    target: dict,
    key: str,
    validation_func=lambda x: True,
    format_func=lambda x: x,
    alt_key: str = None,
):
    """
    Map a source dictionary key-value to a target dictinoary.
    Mapping is parameterized by a source value validation
    function (validation_func) and source to target value
    transformation function (format_func).

    Args:
        source (dict): input dictionary
        target (dict): output dictionary
        key (str):
        alt_key (str, optional):
        validation_func (function):
        format_func (function):
    """
    try:
        value = source.get(key, None)
        valid = value != None and validation_func(value)
        if not valid:
            return False

        formatted_value = format_func(value)

        key = alt_key if alt_key != None else key
        target.update({key: formatted_value})
        return True
    except Exception as inst:
        return False


def map_keys(keys: dict, source: dict, target: dict = None):
    """
    Injective mapping between a source and target dictionary.

    """
    if target == None:
        target = {}
    for key in keys.keys():
        map_tuple = keys.get(key)
        #print(f'map_tuple', key, map_tuple)
        validate_func = map_tuple[0]
        format_func = map_tuple[1]
        alt_key = map_tuple[2] if len(map_tuple) == 3 else None
        map_key(source, target, key, validate_func, format_func, alt_key)
    return target
