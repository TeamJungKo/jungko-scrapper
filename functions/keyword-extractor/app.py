from krwordrank.word import KRWordRank
from query_services import save_extracted_words_to_database
from query_services import get_new_products_from_database
from db_config import create_connection


def task_handler(event, context):
    try:
        # 데이터베이스 연결
        connection = create_connection()

        product_list = get_new_products_from_database(connection)

        for product in product_list:

            # 데이터베이스에서 product 카테고리의 title과 content 가져오기
            content_array = [product.product_content.split('\n')]
            title_array = [product.product_title.split('\n')]

            # 가져온 데이터를 texts에 추가, 제목은 두번 추가
            texts = []
            for content, title in zip(content_array, title_array):
                texts.extend(content)
                texts.extend(title)
                texts.extend(title)

            # KRWordRank 객체 생성
            wordrank_extractor = KRWordRank(min_count=2, max_length=10)

            # extract 메서드로 키워드 추출
            keywords, rank, graph = wordrank_extractor.extract(
                texts, beta=0.85, max_iter=10)

            # 추출된 키워드 중 상위 5개 선택
            selected_keywords = [word for word, r in sorted(
                keywords.items(), key=lambda x: x[1], reverse=True)[:5]]

            # 결과 출력
            print(f'\n추출된 키워드 수: \n{selected_keywords.count}\n')

            # 추출된 키워드를 데이터베이스에 저장
            save_extracted_words_to_database(
                connection, product.product_id, selected_keywords)

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
