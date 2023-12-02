import json
import sys
from db_config import create_connection
from crawler_dang import crawl_dang


def task_handler(event, context):
    try:
        connection = create_connection()
        print('DB Connection created')
        connection.begin()
        print('Connection started')

        crawl_dang(connection)
        print("당근 끝~~")

    except Exception as e:
        print(e)
        connection.rollback()
        print('Connection rollbacked')
        return {'success': False}

    finally:
        print('Connection commited')
        connection.close()
        print('Connection closed')
        return {'success': True}
