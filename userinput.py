import logging
import utils
import database as db
import TMDB
import datetime


def getSerie():
    """
    :return: None or dict_keys(*)
    """
    utils.clear()
    tvshows = database.getAllSeries()
    if len(tvshows) == 0:
        print("Não há series adicionadas")
        utils.pause()
        return None
    print("Séries disponíveis:")
    for k, tvshow in enumerate(tvshows):
        print("%d - %s" % (k + 1, tvshow["ser_nome"]),
              "*" if tvshow["ser_firstadd"] == 1 else "** -> %s" % tvshow["ser_uatualizado"].strftime("%d-%m-%Y %H:%M:%S") if (datetime.datetime.now() - tvshow["ser_uatualizado"]) > datetime.timedelta(hours=3) else "")
    print("* não finalizou primeira adição")
    print("** não foi atualizado recentemente")
    try:
        choice = int(input("\nInforme o número da serie: \n>>"))
    except ValueError:
        return None
    except:
        logger.exception("Error ocurred while picking serie.")
    else:
        if 0 < choice <= len(tvshows):
            return tvshows[choice - 1]
        else:
            return None


def getSeason():
    """
    :return: None or dict_keys(* from serie + epi_temporada)
    """
    serie = getSerie()  # dict_keys(* from serie)
    if serie is None:
        return None
    utils.clear()
    print("Série selecionada: '%s'" % serie['ser_nome'])
    try:
        season = int(input("Informe a temporada: "))
    except ValueError:
        print("Erro ao digitar o valor, retornando...")
    except:
        print("Um erro inesperado ocorreu, retornando...")
        logger.exception("Erro ao captar entrada do usuario")
    else:
        serie["epi_temporada"] = season
        return serie
    utils.pause()
    return None


def getEpisode():
    """
    :return: None or dict_keys(* from serie + epi_temporada + epi_episodio)
    """
    season = getSeason()  # dict_keys(* from serie + epi_temporada)
    if season is None:
        return None
    utils.clear()
    print("Série selecionada: '%s'" % season['ser_nome'])
    print("Temporada selecionada: '%s'" % season["epi_temporada"])
    try:
        episode = int(input("Informe o episódio: "))
    except ValueError:
        print("Erro ao digitar o valor, retornando...")
    except:
        print("Um erro inesperado ocorreu, retornando...")
        logger.exception("Erro ao captar entrada do usuario")
    else:
        season["epi_episodio"] = episode
        return season
    utils.pause()
    return None


def confirm():
    check = None
    while check is None:
        check = input("Confirmar [s/n]\n>>").lower()
        if check == 's':
            return True
        elif check == 'n':
            return False
        check = None
    return False


logger = logging.getLogger("Program.%s" % __name__)
database = db.Database()
tmdb = TMDB.TMDB()

if __name__ == "__main__":
    print(getEpisode())
