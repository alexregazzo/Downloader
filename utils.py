import os


def clear():
    os.system("cls")


def pause():
    os.system("pause")


def dictInList(dictionary, array, keys_to_compare=None):
    """
    :param dictionary: dict to check if it is in list
    :param array: list of dicts that may contain the dict
    :param keys_to_compare: [str, ...] that has the keys to evaluate, default is None which will be the keys of dictionary
    :return: False if key doesnt exist in both dict in comparison or the comparisions results in different values, True if equal
    """
    if keys_to_compare is None:
        keys_to_compare = dictionary.keys()
    for v in array:
        isEqual = True
        for key in keys_to_compare:
            try:
                if v[key] != dictionary[key]:
                    isEqual = False
            except:
                isEqual = False
        if isEqual:
            return True
    return False


def removeProblematicChars(string):
    return string.replace("'", "")


if __name__ == "__main__":
    pass
    # dictInList({"a": 3}, [{}, {"b"}], keys_to_compare=['a', 'b'])
