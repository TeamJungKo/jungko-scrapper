
import pymysql
from models import Notification

"""
    모든 지역 정보를 조회한다.
    조회된 지역 정보를 바탕으로 지역 id를 key로, 지역 이름을 value로 하는 dict를 생성하여 반환한다.
"""


def find_all_areas(connection: pymysql.Connection) -> dict:
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("""
            SELECT emd_area.id as id, sido_area.name as sido, sigg_area.name as sigg, emd_area.name as emd
            FROM emd_area
            INNER JOIN sigg_area ON emd_area.sigg_area_id = sigg_area.id
            INNER JOIN sido_area ON sigg_area.sido_area_id = sido_area.id;
        """)
        areas = cursor.fetchall()
        return {row['id']: f"{row['sido']} {row['sigg']} {row['emd']}" for row in areas}


"""
    알림 수신을 동의한 회원들 중 새 상품에 대한 관심 키워드를 구독하고 있는 회원 정보를 조회한다.
    조회된 회원 정보를 바탕으로 Notification 객체 list를 생성하여 반환한다.
"""


def create_notifications_for_new_product_subscribers(connection: pymysql.Connection, areas: dict) -> list[Notification]:
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("""
            SELECT m.id, m.nickname, m.email, m.device_token,
                p.title, ik.keyword, p.area_id, p.id as product_id
            FROM member m
                    INNER JOIN interested_keyword ik ON m.id = ik.member_id
                    INNER JOIN product_keyword pk ON ik.keyword = pk.keyword
                    INNER JOIN product p ON pk.product_id = p.id
            WHERE p.is_new=true
            AND m.notification_agreement=true;
                """)
        new_products = cursor.fetchall()
        notifications = [Notification(
            target_member_id=raw_data['id'],
            target_member_nickname=raw_data['nickname'],
            target_member_email=raw_data['email'],
            device_token=raw_data['device_token'],
            notice_title=f"[{raw_data['keyword']} 키워드 알림] {areas[raw_data['area_id']]}",
            notice_content=raw_data['title'],
            product_id=raw_data['product_id']
        ) for raw_data in new_products]
        return notifications


def save_notifications(connection: pymysql.Connection, notifications: list[Notification]):
    notification_dicts = [
        {
            'notice_title': notification.notice_title,
            'notice_content': notification.notice_content,
            'product_id': notification.product_id,
            'target_member_id': notification.target_member_id
        } for notification in notifications
    ]
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.executemany("""
            INSERT INTO notification (title, content, product_id, is_read, created_at, member_id)
            VALUES (%(notice_title)s, %(notice_content)s, %(product_id)s, false, now(), %(target_member_id)s);
        """, notification_dicts)
        connection.commit()


def set_product_is_new(connection: pymysql.Connection, is_new: bool):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("""
            UPDATE product SET is_new=%s WHERE is_new != %s;
        """, (is_new, is_new))
        connection.commit()
