import os
import pymysql

db_settings = {
    "host": os.getenv('MARIADB_HOST'),
    "user": os.getenv('MARIADB_USER'),
    "password": os.getenv('MARIADB_PASSWORD'),
    "db": os.getenv('MARIADB_DATABASE'),
    "port": int(os.getenv('MARIADB_PORT')),
    "charset": 'utf8mb4',
}


def create_connection() -> pymysql.Connection:
    connection = pymysql.connect(
        host=db_settings['host'],
        user=db_settings['user'],
        password=db_settings['password'],
        db=db_settings['db'],
        port=db_settings['port']
    )
    return connection
