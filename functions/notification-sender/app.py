from query_services import find_all_areas, create_notifications_for_new_product_subscribers
from db_config import create_connection


def task_handler(event, context):
    try:
        connection = create_connection()
        area_dict = find_all_areas(connection)
        notifications = create_notifications_for_new_product_subscribers(
            connection, area_dict)
        print(notifications)
    except Exception as e:
        print(e)
        return {'success': False}
    finally:
        connection.close()
        print('Connection closed')
        return {'success': True}
