import os
import sys

try:
    import json
except:
    print("Um erro ocorreu ao iniciar alguns módulos")
    os.system("pause")
    sys.exit(1)

print("Voce precisa ter instalado utorrent para que o programa funcione")
os.system("pause")

if not os.path.exists("userconfig"):
    os.mkdir("userconfig")
print("Você precisa de uma chave de acesso a API do TMDB(https://www.themoviedb.org/)")
tmdb_api_key = input("Insira a chave de acesso da API:")

try:
    with open("userconfig/tmdb.json", "w") as f:
        json.dump({"KEY": tmdb_api_key}, f)
except Exception as e:
    print("Um erro ocorreu ao salvar a chave de acesso")
    print(e)
    os.system("pause")
    sys.exit(1)

resp = input("Deseja instalar alguns módulos necessários? [s/n]").lower()
if resp != 's':
    print("Saindo...")
    os.system("pause")
    sys.exit(0)
os.system("pip install -r requirements.txt")
print("Instalação de pacotes finalizada!")
print("Configuração do banco de dados:")
print("O banco de dados a ser utilizado é o mysqlserver da microsoft diponível em: https://dev.mysql.com/downloads/mysql/ ")
print("Além disso, deve estar instalado o mysql.connector disponível em: https://dev.mysql.com/downloads/connector/python/")
resp = input("Os programas foram instalados?[s/n]").lower()
if resp != 's':
    print("Instale e inicie o setup novamente")
    print("Saindo...")
    os.system("pause")
    sys.exit(0)

try:
    import mysql.connector
except ModuleNotFoundError:
    print("O módulo mysql.connector não foi encontrado, instale-o e inicie novamente.")
    print("Saindo...")
    os.system("pause")
    sys.exit(0)
else:
    print("Configurando a conexão com o banco de dados:")
    host = input("Informe o host do banco de dados (ex: localhost): ")
    user = input("Informe o usuario do banco de dados (ex: root): ")
    passwd = input("Informe a senha do banco de dados: ")
    database = input("Informe o nome do banco de dados (ex: serie):")

    print(f"host: {host}, user: {user}, password:{passwd}, database: {database}")
    resp = input("Salvar? [s/n]").lower()
    if resp != 's':
        print("Não salvo. Saindo...")
        os.system("pause")
        sys.exit(0)
    try:
        database = {
            "database": {
                "release": {
                    "host": host,
                    "user": user,
                    "passwd": passwd,
                    "database": database
                }
            }
        }
        with open("userconfig/database.json", "w") as f:
            json.dump(database, f)
    except Exception as e:
        print("Um erro desconhecido ocorreu:")
        print(e)
        print("Saindo")
        os.system("pause")
        sys.exit(1)
    else:
        print("Salvo com sucesso")
        print("Iniciando testes de conexão")
        try:
            dbname = database['database']['release']['database']
            del database['database']['release']['database']
            print("Inicio")
            conn = mysql.connector.connect(**database["database"]["release"])
            print("Sucesso 1/20")
            cursor = conn.cursor()
            print("Sucesso 2/20")
            cursor.execute(f"DROP DATABASE IF EXISTS {dbname}")
            print("Sucesso 3/20")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbname}")
            print("Sucesso 4/20")
            conn.close()
            print("Sucesso 5/20")
            conn = mysql.connector.connect(**database["database"]["release"], database=dbname)
            print("Sucesso 6/20")
            cursor = conn.cursor()
            print("Sucesso 7/20")
            cursor.execute("drop table if exists testtable")
            print("Sucesso 8/20")
            cursor.execute("create table testtable(a int)")
            print("Sucesso 9/20")
            cursor.execute("insert into testtable(a)values (1)")
            print("Sucesso 10/20")
            cursor.execute("select * from testtable")
            print("Sucesso 11/20")
            test_data = cursor.fetchall()
            print("Sucesso 12/20")
            if len(test_data) == 1:
                print("Sucesso 13/20")
                if test_data[0] == (1,):
                    print("Sucesso 14/20")
                    cursor.execute("DROP TABLE testtable")
                    print("Sucesso 15/20")
                    conn.close()
                    print("Sucesso 16/20")
                    conn = mysql.connector.connect(**database["database"]["release"], database=dbname)
                    print("Sucesso 17/20")
                    cursor = conn.cursor()
                    print("Sucesso 18/20")
                    cursor.execute(f"DROP DATABASE IF EXISTS {dbname}")
                    print("Sucesso 19/20")
                    conn.close()
                    print("Sucesso 20/20")
                    
                else:
                    raise Exception("Wrong data")
            else:
                raise Exception("Wrong length")
        except Exception as e:
            print("Um erro ocorreu")
            print(e)
            os.system("pause")
            sys.exit(1)
print("Setup finalizado")
os.system("pause")
