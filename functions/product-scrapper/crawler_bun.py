import requests
from bs4 import BeautifulSoup
import pymysql
from db_services import find_category_bun, find_area, is_market_product_id_onDB, create_product, save_product


def crawl_bun(connection: pymysql.Connection):
    # API로 카테고리 조회 후 사용할 카테고리를 리스트로 가공
    category_url = 'https://api.bunjang.co.kr/api/1/categories/list.json'
    req = requests.get(category_url)
    raw_category = req.json()
    raw_category_list = raw_category['categories']
    category_list = []
    for category in raw_category_list:
        if 'categories' in category and category['categories']:
            subCategories = category['categories']
            for subCategory in subCategories:
                category_list.append(subCategory['id'])

    for category in category_list:
        extract_data(connection, category)


def extract_data(connection: pymysql.Connection, categoryId):
    url = 'https://api.bunjang.co.kr/api/1/find_v2.json?f_category_id=' + categoryId + \
        '&page=0&order=date&req_ref=popular_category&request_id=20231203171516&stat_device=w&n=100&version=4'
    req = requests.get(url)
    raw_data = req.json()
    data = raw_data['list']

    market_name = '번개장터'

    # 카테고리 정보는 결정난 상태이므로 바로 할당
    category_id = find_category_bun(categoryId)

    for product in data:
        # 마켓 Id 추출
        market_product_id = product['pid']

        # 이미지 url 추출
        imageUrl = product['product_image']

        # 제목 추출
        title = product['name']

        # 가격 추출
        price = product['price']

        # 지역 추출
        raw_area = product['location']
        if raw_area == '':
            area = '불명'
            area_id = 0
        else:
            area = raw_area.split()[-1]
            area_id = find_area(connection, area)

        # 내용 추출
        content = ''

        product_info = {
            'imageUrl': imageUrl,
            'area': area_id,
            'title': title,
            'category': category_id,
            'price': price,
            'content': content
        }

        # DB에서 market_product_id 조회 후 중복시 해당 루프 스킵
        if (is_market_product_id_onDB(connection, market_product_id)):
            print('Skip this product : Already on DB => ' +
                  market_product_id + '\n\n')
            continue

        # 데이터로 product 생성
        product = create_product(
            product_info, market_product_id, market_name)
        print('Successfully Created')

        print(product)

        # 물건 이외의 카테고리라면 해당 루프 스킵
        if (category_id == 0):
            print('Skip this product : This is not product' + '\n\n')
            continue

        # 만약 읍면동 조회 불가라면 해당 루프 스킵
        if (area_id == 0):
            print('Skip this product : No area Info in DB => ' + area + '\n\n')
            continue

        # DB에 product 생성
        save_product(connection, product)
        print("Successfully Saved" + '\n\n')
