from query_services import find_all_areas, create_notifications_for_new_product_subscribers, save_notifications, set_product_is_new
from db_config import create_connection
from fcm_sender import send_notification


def task_handler(event, context):
    try:
        connection = create_connection()
        print('DB Connection created')
        connection.begin()
        print('Connection started')

        area_dict = find_all_areas(connection)
        print('Areas founded')

        notifications = create_notifications_for_new_product_subscribers(
            connection, area_dict)
        print('Notifications created')

        send_notification(notifications)

        save_notifications(connection, notifications)
        print('Notifications saved')

        set_product_is_new(connection, False)
        print('Products updated')
        connection.commit()
        print('Connection commited')
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
