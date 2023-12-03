import requests
from bs4 import BeautifulSoup
import pymysql
from db_services import find_category_jung, find_area, is_market_product_id_onDB, create_product, save_product


def crawl_jung(connection: pymysql.Connection):
    # 카테고리 리스트 생성 146,245, 246 제외 101 ~ 261 + 1349, 1350 포함
    category_list = list(range(101, 262))
    category_list.remove(146)
    category_list.remove(244)
    category_list.remove(245)
    category_list.extend([1349, 1350])

    for category in category_list:
        extract_data(connection, category)


def extract_data(connection: pymysql.Connection, categoryId):
    categoryNum = str(categoryId)

    url = 'https://web.joongna.com/_next/data/5vLYEQ5wI7xPDg2f6IWK5/search.json?category=' + \
        categoryNum + '&page=1'
    req = requests.get(url)
    raw_data = req.json()
    products = raw_data['pageProps']['dehydratedState']['queries'][0]['state']['data']['data']['items']

    market_name = '중고나라'

    # 카테고리 정보는 결정난 상태이므로 바로 할당
    category_id = find_category_jung(categoryNum)

    for product in products[:8]:
        # 마켓 Id 추출
        market_product_id = product['seq']

        # 이미지 url 추출
        imageUrl = product['url']

        # 제목 추출
        title = product['title']

        # 가격 추출
        price = product['price']

        # 지역 추출
        raw_area = product['mainLocationName']
        if raw_area == '':
            area = '불명'
            area_id = 0
        else:
            area = raw_area
            area_id = find_area(connection, raw_area)

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
                  str(market_product_id) + '\n\n')
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
