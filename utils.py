import os
import re


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


from unicodedata import normalize


def remove_non_ascii(txt):
    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')


def get_specs_from_name(txt):
    """
    :param txt: name of the file
    If any of the 3 episode especificatoin is not found, returns None
    :return: None or dict_kets([ser_nome, epi_temporada, epi_episodio])
    """
    try:
        txt = remove_non_ascii(txt).strip().lower()
        txt = " ".join(re.split("['. -]", txt))
        match = re.match("^(\w+.*) s(\d\d+)e(\d\d+).*$", txt)
        if match is not None:
            name, season, episode = match.groups()
            return {"ser_nome": name.strip().title(), "epi_temporada": int(season), "epi_episodio": int(episode)}
        match = re.match("^((?:[a-z0-9]+ )+?)(\d{3,4}).*$", txt)
        if match is not None:
            name, season_episode = match.groups()
            if len(season_episode) == 3:
                season = season_episode[0]
                episode = season_episode[1:3]
            elif len(season_episode) == 4:
                season = season_episode[0:2]
                episode = season_episode[2:4]
            else:
                return None
            return {"ser_nome": name.strip().title(), "epi_temporada": int(season), "epi_episodio": int(episode)}
        return None
    except:
        return None


if __name__ == "__main__":
    pass