CREATE TABLE IF NOT EXISTS serie
(
    ser_id          integer NOT NULL,
    ser_nome        text    NOT NULL,
    ser_poster      text             DEFAULT NULL,
    ser_uatualizado text    NOT NULL DEFAULT '1900-01-01 00:00:00',
    ser_adicionado  text    NOT NULL,
    ser_firstadd    integer NOT NULL DEFAULT 1 check (ser_firstadd in (0, 1)),
    PRIMARY KEY (ser_id)
);

CREATE TABLE IF NOT EXISTS episodio
(
    ser_id           integer NOT NULL,
    epi_temporada    integer NOT NULL,
    epi_episodio     integer NOT NULL,
    epi_lancamento   text    NOT NULL,
    epi_baixar       integer NOT NULL DEFAULT 1 check (epi_baixar in (0, 1)),
    epi_uatualizacao text    NOT NULL DEFAULT '1900-01-01 00:00:00',
    epi_adicionado   text    NOT NULL,
    PRIMARY KEY (ser_id, epi_temporada, epi_episodio),
    FOREIGN KEY (ser_id) REFERENCES serie (ser_id)
);

CREATE TABLE IF NOT EXISTS link
(
    lin_id         integer NOT NULL primary key autoincrement,
    ser_id         integer NOT NULL,
    epi_temporada  integer NOT NULL,
    epi_episodio   integer NOT NULL,
    lin_nome       text    NOT NULL,
    lin_link       text    NOT NULL,
    lin_baixando   integer NOT NULL DEFAULT 0 check ( lin_baixando in (0, 1)),
    lin_baixado    integer NOT NULL DEFAULT 0 check (lin_baixado in (0, 1)),
    lin_adicionado text    NOT NULL,
--     lin_baixadoem      text    NULL,
--     lin_popularidade   integer NULL,
--     lin_nota_usuario   integer NULL,
--     lin_nota_calculada integer NULL,

    FOREIGN KEY (ser_id, epi_temporada, epi_episodio)
        REFERENCES episodio (ser_id, epi_temporada, epi_episodio)
--     CHECK (lin_nota_usuario BETWEEN 0 AND 10),
--     CHECK (lin_nota_calculada BETWEEN 0 AND 10)
);