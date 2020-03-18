CREATE TABLE IF NOT EXISTS serie (
  ser_id INT NOT NULL,
  ser_nome VARCHAR(150) NOT NULL,
  ser_poster VARCHAR(100) NULL DEFAULT NULL,
  ser_uatualizado DATETIME NOT NULL DEFAULT '1900-01-01 00:00:00',
  ser_adicionado DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ser_firstadd BOOL NOT NULL DEFAULT 1,
  PRIMARY KEY (ser_id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;

CREATE TABLE IF NOT EXISTS episodio (
  ser_id INT NOT NULL,
  epi_temporada INT NOT NULL,
  epi_episodio INT NOT NULL,
  epi_lancamento DATE NOT NULL,
  epi_baixar BOOL NOT NULL DEFAULT TRUE,
  epi_uatualizacao DATETIME NOT NULL DEFAULT '1900-01-01 00:00:00',
  epi_adicionado DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (ser_id, epi_temporada, epi_episodio),
  CONSTRAINT fk_EPISODIO_SERIE
    FOREIGN KEY (ser_id)
    REFERENCES series.serie (ser_id))
  ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;


CREATE TABLE IF NOT EXISTS link (
    lin_id INT NOT NULL AUTO_INCREMENT,
    ser_id INT NOT NULL,
    epi_temporada INT NOT NULL,
    epi_episodio INT NOT NULL,
    lin_nome VARCHAR(150) NOT NULL,
    lin_link VARCHAR(500) NOT NULL,
    lin_baixando BOOL NOT NULL DEFAULT 0,
    lin_baixado BOOL NOT NULL DEFAULT 0,
    lin_baixadoem DATETIME NULL,
    lin_popularidade INT NULL,
    lin_nota_usuario INT NULL,
    lin_nota_calculada INT NULL,
    lin_adicionado DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (lin_id),
    CONSTRAINT fk_LINK_EPISODIO FOREIGN KEY (ser_id , epi_temporada , epi_episodio)
        REFERENCES episodio (ser_id , epi_temporada , epi_episodio),
    CONSTRAINT check_link_nota_usuario CHECK (lin_nota_usuario BETWEEN 0 AND 10),
    CONSTRAINT check_link_nota_calculada CHECK (lin_nota_calculada BETWEEN 0 AND 10))
    ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4;