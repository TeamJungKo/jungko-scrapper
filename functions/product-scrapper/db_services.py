import pymysql
import datetime


# 당근인 경우 카테고리
def find_category_dang(category_name: str):
    if category_name == '디지털기기':
        return 49
    elif category_name == '가구/인테리어':
        return 130
    elif category_name == '유아동':
        return 166
    elif category_name == '여성의류':
        return 2
    elif category_name == '여성잡화':
        return 40
    elif category_name == '남성패션/잡화':
        return 10
    elif category_name == '생활가전':
        return 81
    elif category_name == '생활/주방':
        return 143
    elif category_name == '가공식품':
        return 157
    elif category_name == '스포츠/레저':
        return 187
    elif category_name == '취미/게임/음반':
        return 93
    elif category_name == '뷰티/미용':
        return 120
    elif category_name == '식물':
        return 130
    elif category_name == '반려동물용품':
        return 174
    elif category_name == '티켓/교환권':
        return 115
    elif category_name == '도서' or '유아도서':
        return 111
    else:  # 기타 중고물품
        return 1


# DB에 없는 읍면동이라면 해당 상품은 저장 제외 => crawler에서 로직 구현
def find_area(connection: pymysql.Connection, emd_name: str):
    with connection.cursor() as cursor:
        sql = "SELECT id FROM emd_area WHERE name = %s"
        cursor.execute(sql, emd_name)
        result = cursor.fetchone()
        return int(result[0]) if result else 0


def is_market_product_id_onDB(connection: pymysql.Connection, market_product_id: str):
    try:
        with connection.cursor() as cursor:
            # 테이블 이름과 컬럼 이름은 예시로 사용됩니다. 실제 값으로 변경해야 합니다.
            sql = "SELECT EXISTS(SELECT 1 FROM product WHERE market_product_id = %s)"
            cursor.execute(sql, market_product_id)
            result = cursor.fetchone()
            return bool(result[0])  # 결과가 존재하면 True, 그렇지 않으면 False 반환
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
        return False  # 데이터베이스 오류 발생시 False 반환


# 기존 product 관련 딕셔너리에 마켓 id와 마켓 이름 추가
def create_product(product_info: dict, market_product_id: int, market_name: str):
    product_info["market_product_id"] = market_product_id
    product_info["market_name"] = market_name
    product_info['created_at'] = datetime.datetime.now()
    product_info['uploaded_at'] = datetime.datetime.now()
    return product_info


# created_at, updated_at, is_new는 어떻게?
def save_product(connection: pymysql.Connection, data: dict):
    with connection.cursor() as cursor:
        sql = """
        INSERT INTO product (availability, content, created_at, image_url, market_name, market_product_id, price, title, uploaded_at, area_id, product_category_id, is_new) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, ('ON_SALE', data['content'], data['created_at'], data['imageUrl'], data['market_name'], data['market_product_id'], data['price'],
                       data['title'], data['uploaded_at'], data['area'], data['category'], True))
        connection.commit()
