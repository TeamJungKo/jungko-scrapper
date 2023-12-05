import pymysql
from product_models import Product
from typing import List


# 데이터베이스에서 Product 데이터를 조회하는 함수
def get_new_products_from_database(connection: pymysql.Connection) -> List[Product]:
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("""
            SELECT id, title, content, is_new
            FROM product
            WHERE is_new = 1
        """)
        results = cursor.fetchall()

    products = []
    for result in results:
        product = Product(
            product_id=result['id'],
            product_title=result['title'],
            product_content=result['content']
        )
        products.append(product)

    return products


#추출된 단어를 데이터베이스에 저장하는 함수
def save_extracted_words_to_database(connection: pymysql.Connection, product_id: int, words: List[str]):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        try:
            for word in words:
                sql_query = """
                    INSERT INTO product_keyword (product_id, keyword)
                    VALUES (%s, %s);
                """
                executed_query = cursor.mogrify(sql_query, (product_id, word))
                print("Executing SQL Query:", executed_query)
                cursor.execute(sql_query, (product_id, word))
                
                # execute() 호출 성공 여부 확인
                if cursor.rowcount > 0:
                    print("Query executed successfully.")
                    
                    # connection이 열려 있는지 확인
                    if not connection.open:
                        print("Connection is closed. Reconnecting...")
                        connection.connect()
                    
                    # commit을 호출
                    connection.commit()
                else:
                    print("Query execution failed.")
                    connection.rollback()
        except Exception as e:
            print("Error occurred:", e)
            connection.rollback()
