import logging
import shutil
import os
from scripts import TMDB, userinput, utils, settings, database as db
import datetime


def adicionarSerie():
    utils.clear()
    print("Informe o nome da série")
    name = input(">>")
    utils.clear()
    acquired = tmdb.lock.acquire(blocking=False)
    if not acquired:
        print("Aguarde...")
    while not acquired:
        acquired = tmdb.lock.acquire(blocking=False)
    results = tmdb.searchTVShow(name=name)
    tmdb.lock.release()
    if len(results) == 0:
        print("Nenhum resultado encontrado para '{}'".format(name))
    else:
        print("{} resultados encontrados para {}".format(len(results['results']), name))
        for k, serie in enumerate(results['results']):
            print("*" * 50)
            print("Idenfitificador: {}".format(k + 1))
            print("Nome: {original_name}".format(**serie))
            print("*" * 50)
        print("Informe o identificador da serie que deseja adicionar: ")
        try:
            op = int(input(">>"))
        except ValueError:
            pass
        else:
            if op < 1:
                print("Saindo...")
                utils.pause()
                return
            elif op <= len(results):
                if database.addSerie(results['results'][op - 1]['id'], results['results'][op - 1]['original_name']):
                    print("Serie adicionada com sucesso!")
                else:
                    print("Serie não adicionada!")
                utils.pause()


def removeSerie():
    utils.clear()
    series = database.getAllSeries()  # dict_keys(* from serie)
    if len(series) == 0:
        print("Não há series adicionadas.")
        utils.pause()
        return
    else:
        for k, serie in enumerate(series):
            print("*" * 50)
            print("Identificador: {}".format(k + 1))
            print("Nome: {}".format(serie["ser_nome"]))
            print("*" * 50)
        print("Informe o identificador")
        try:
            op = int(input(">>"))
        except ValueError:
            pass
        else:
            if 0 < op <= len(series):
                logger.debug(f"Trying to remove: {series[op - 1]['ser_id']}")
                if database.removeSerie(series[op - 1]["ser_id"]):
                    print("Série removida com sucesso")
                    logger.debug("Removed")
                else:
                    print("Houve algum erro durante a remoção!")
                    logger.warning("Problem on removing")
            else:
                print("Operação cancelada.")
    utils.pause()


def listtodownloadepisodes():
    episodios = database.getToDownloadEpisode()  # [dict_keys(ser_id, ser_nome, epi_temporada, epi_episodio)]
    if len(episodios) == 0:
        print("Não há episódios para baixar")
    for episodio in episodios:
        print("{} - S{:0>2d} E{:0>2d}".format(episodio["ser_nome"], episodio["epi_temporada"], episodio["epi_episodio"]))
    utils.pause()


def listseries():
    series = database.getAllSeries()
    if len(series) == 0:
        print("Não há series adicionadas")
    for serie in series:
        print("{}".format(serie["ser_nome"]))
    utils.pause()


def downloadEpisode():
    episode = userinput.getEpisode()  # dict_keys(* from serie, epi_temporada, epi_episodio)
    if episode is None:
        print("Operação cancelada!")
        utils.pause()
        return
    utils.clear()
    print("Baixar episódio:")
    print("Série: %s" % episode['ser_nome'])
    print("Temporada: %s" % episode['epi_temporada'])
    print("Episódio: %s" % episode['epi_episodio'])
    if userinput.confirm():
        if database.setDownloadEpisodeAs(episode["ser_id"], episode["epi_temporada"], episode["epi_episodio"], True):
            print("Concluido com sucesso!")
            logger.info("Sucesso ao definir para baixar episodio '%s'" % str(episode))
        else:
            print("Houve um erro ao realizar a ação no banco de dados! Tente mais tarde!")
            logger.warning("Erro ao definir episodio para baixar")
    else:
        print("operação cancelada!")
    utils.pause()


def downloadAfter():
    episode = userinput.getEpisode()  # None or dict_keys(* from serie + epi_temporada + epi_episodio)
    if episode is None:
        print("Operação cancelada!")
        utils.pause()
        return
    utils.clear()
    print("Baixar todos os episódios a partir de:")
    print("Série: %s" % episode['ser_nome'])
    print("Temporada: %s" % episode['epi_temporada'])
    print("Episódio: %s" % episode['epi_episodio'])
    if userinput.confirm():
        if database.setToDownloadAfterEpisodeAs(episode["ser_id"], episode["epi_temporada"], episode["epi_episodio"], True):
            print("Concluido com sucesso!")
            logger.info("Sucesso ao definir para baixar episodios a partir de '%s'" % str(episode))
        else:
            print("Houve um erro ao realizar a ação no banco de dados! Tente mais tarde!")
            logger.warning("Erro ao definir episodio para baixar a partir de")
    else:
        print("operação cancelada!")
    utils.pause()


def recentlyadded():
    utils.clear()
    episodios = database.getRecentlyAddedEpisodes()  # [dict_keys(ser_nome, epi_temporada, epi_episodio, epi_adicionado), ... ]
    episodios.reverse()  # least recent to most recent
    size = database.getMinMaxSizeOfSerieNames()
    if len(episodios) == 0:
        print("Não há episodios adicionados nas ultimas 3 horas")
        utils.pause()
        return
    if size is None:
        logger.critical("Something is not right! size cannot be none if there is something on the table")
        print("Um erro inesperado aconteceu!")
        utils.pause()
        return
    print("Episódios adicionados nas ultimas 3 horas")
    for episodio in episodios:
        print("{: <{width}} S{:02}E{:02}   {}".format(episodio["ser_nome"], episodio["epi_temporada"], episodio["epi_episodio"], episodio["epi_adicionado"],
                                                      width=size[1] + 2))
    utils.pause()


def lastadded():
    utils.clear()
    episodios = database.getLastAddedEpisodes()  # [dict_keys(ser_nome, epi_temporada, epi_episodio, epi_adicionado), ... ]
    episodios.reverse()  # least recent to most recent
    size = database.getMinMaxSizeOfSerieNames()
    if len(episodios) == 0:
        print("Não há episodios adicionados")
        utils.pause()
        return
    if size is None:
        logger.critical("Something is not right! size cannot be none if there is something on the table")
        print("Um erro inesperado aconteceu!")
        utils.pause()
        return
    print("Ultimos {} episódios adicionados".format(len(episodios)))
    for episodio in episodios:
        print("{: <{width}} S{:02}E{:02}   {}".format(episodio["ser_nome"], episodio["epi_temporada"], episodio["epi_episodio"], episodio["epi_adicionado"],
                                                      width=size[1] + 2))
    utils.pause()


def listmenu():
    while True:
        utils.clear()
        print("** Listar menu **")
        print("0 - Voltar")
        print("1 - Series")
        print("2 - Episodios para baixar")
        print("3 - Episodios adicionados recentemente")
        print("4 - Ultimos episódios adicionados")
        try:
            op = int(input("O que deseja listar?\n>>"))
        except ValueError:
            pass
        else:
            utils.clear()
            if op == 1:
                # mostrar series
                listseries()
            elif op == 2:
                # mostrar to download episodes
                listtodownloadepisodes()
            elif op == 3:
                recentlyadded()
            elif op == 4:
                lastadded()
            else:
                break


def downloadmenu():
    while True:
        utils.clear()
        print("** Download menu **")
        print("0 - Voltar")
        print("1 - Baixar a partir de")
        print("2 - Baixar episodio")
        try:
            op = int(input("Informe a opção?\n>>"))
        except ValueError:
            pass
        else:
            utils.clear()
            if op == 1:
                downloadAfter()
            elif op == 2:
                downloadEpisode()
            else:
                break


def undownloadAfter():
    episode = userinput.getEpisode()  # None or dict_keys(* from serie + epi_temporada + epi_episodio)
    if episode is None:
        print("Operação cancelada!")
        utils.pause()
        return
    utils.clear()
    print("Remover todos os episódios a partir de:")
    print("Série: %s" % episode['ser_nome'])
    print("Temporada: %s" % episode['epi_temporada'])
    print("Episódio: %s" % episode['epi_episodio'])
    if userinput.confirm():
        if database.setToDownloadAfterEpisodeAs(episode["ser_id"], episode["epi_temporada"], episode["epi_episodio"], False):
            print("Concluido com sucesso!")
            logger.debug("Sucesso ao definir para remover de baixar episodios a partir de '%s'" % str(episode))
        else:
            print("Houve um erro ao realizar a ação no banco de dados! Tente mais tarde!")
            logger.warning("Erro ao definir episodio para baixar a partir de")
    else:
        print("operação cancelada!")
    utils.pause()


def undownloadEpisode():
    episode = userinput.getEpisode()  # dict_keys(* from serie, epi_temporada, epi_episodio)
    if episode is None:
        print("Operação cancelada!")
        utils.pause()
        return
    utils.clear()
    print("Remover download episódio:")
    print("Série: %s" % episode['ser_nome'])
    print("Temporada: %s" % episode['epi_temporada'])
    print("Episódio: %s" % episode['epi_episodio'])
    if userinput.confirm():
        if database.setDownloadEpisodeAs(episode["ser_id"], episode["epi_temporada"], episode["epi_episodio"], False):
            print("Concluido com sucesso!")
            logger.debug("Sucesso ao definir para não baixar episodio '%s'" % str(episode))
        else:
            print("Houve um erro ao realizar a ação no banco de dados! Tente mais tarde!")
            logger.warning("Erro ao definir episodio para não baixar")
    else:
        print("operação cancelada!")
    utils.pause()


def undownloadmenu():
    while True:
        utils.clear()
        print("** Remove from download menu **")
        print("0 - Voltar")
        print("1 - Remover a partir de")
        print("2 - Remover episodio")
        try:
            op = int(input("Informe a opção?\n>>"))
        except ValueError:
            pass
        else:
            utils.clear()
            if op == 1:
                undownloadAfter()
            elif op == 2:
                undownloadEpisode()
            else:
                break


def troubleshoot():
    # copy log to desktop
    dp = os.path.join(os.environ["HOMEPATH"], "Desktop")
    fi = 0
    while os.path.isfile(os.path.join(dp, "downloader_log(%s).log" % fi)):
        fi += 1
    shutil.copy("log_debug.log", os.path.join(dp, "downloader_log(%s).log" % fi))
    utils.pause()


def print_to_download():
    episodes = database.getToDownloadEpisodeWithoutLink()  # [dict_keys(ser_id, ser_nome, epi_temporada, epi_episodio, epi_uatualizacao)]
    if len(episodes) == 0:
        return
    print("Episódios aguardando link:")
    tamanho_min, tamanho_max = database.getMinMaxSizeOfSerieNames()
    for episode in episodes:
        next_update = datetime.timedelta(hours=3) - (datetime.datetime.now() - datetime.datetime.strptime(episode['epi_uatualizacao'], settings.DATETIME_FORMAT))
        if next_update.total_seconds() < 0:
            next_update = datetime.timedelta(seconds=0)
        next_update_s = str(int(next_update.seconds % 60)).rjust(2, '0')
        next_update_m = str(int(next_update.seconds / 60) % 60).rjust(2, '0')
        next_update_h = str(int(next_update.seconds / 3600)).rjust(2, '0').rjust(4, " ")
        print("{: <{width}} S{:02}E{:02}   Proxima atualização em: {}:{}:{}".format(episode['ser_nome'], episode['epi_temporada'], episode['epi_episodio'], next_update_h, next_update_m, next_update_s,
                                                                                    width=tamanho_max))


def mainmenu():
    utils.clear()
    print_to_download()
    print("+" * 50)
    print("0 - Sair")
    print("1 - Baixar")
    print("2 - Listar")
    print("3 - Adicionar")
    print("4 - Remover")
    print("5 - Remover de download")
    print("+" * 50)
    print("Informe a opção:")
    try:
        inp = input(">>").lower()
        if inp == "troubleshoot":
            troubleshoot()
        choice = int(inp)
    except ValueError:
        pass
    except:
        logger.exception("Choice exception ocurred.")
    else:
        if choice == 0:  # sair
            logger.info("Exitting")
            print("Saindo...")
            return False
        elif choice == 1:  # baixar
            downloadmenu()
        elif choice == 2:  # listar
            listmenu()
        elif choice == 3:  # adicionar
            adicionarSerie()
        elif choice == 4:  # remover
            removeSerie()
        elif choice == 5: #remover download
            undownloadmenu()
    return True


def run():
    try:
        logger.info("Run")
        while mainmenu():
            pass
    except:
        logger.exception("An error ocurred")
    finally:
        logger.debug("QUITTING USER RUN")


logger = logging.getLogger("Program.%s" % __name__)
database = db.Database()
tmdb = TMDB.TMDB()
if __name__ == "__main__":
    print_to_download()
