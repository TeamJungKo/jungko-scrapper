import requests
from bs4 import BeautifulSoup
import pymysql
from db_services import find_area, find_category_dang, is_market_product_id_onDB, create_product, save_product


def crawl_dang(connection: pymysql.Connection):
    main_url = 'https://www.daangn.com/hot_articles'
    response = requests.get(main_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    market_name = "당근마켓"

    # 'content' 섹션 내부의 'cards-wrap' 섹션 찾기
    cards_wrap = soup.find('section', id='content').find(
        'section', class_='cards-wrap')

    # 각 'card-top' 아티클의 'a' 태그 찾기
    articles = cards_wrap.find_all('article', class_='card-top')
    for article in articles:
        a_tag = article.find('a')
        if a_tag and 'href' in a_tag.attrs:
            try:
                link = 'https://www.daangn.com' + a_tag['href']

                # 추출한 데이터 처리에 market_product_id 추가 => DB에서 string
                market_product_id = link.split('/')[2]

                # DB에서 market_product_id 조회 후 중복시 해당 루프 스킵
                if (is_market_product_id_onDB(connection, market_product_id)):
                    continue

                # 링크로 접근하여 데이터 추출
                article_data = extract_data_from_link(connection, link)

                # 만약 읍면동 조회 불가라면 해당 루프 스킵
                if (article_data['area'] == 0):
                    continue

                # 데이터 종합해서 product 생성
                product = create_product(
                    article_data, market_product_id, market_name)
                print('Successfully Created')

                # DB에 product 생성
                save_product(connection, product)
                print("Successfully Saved")

            except Exception as e:
                print(e)
                connection.rollback()
                print('Creation rollbacked')


# hot_articles에 있는 링크를 인자로 받아서 해당 링크에서 데이터 추출
def extract_data_from_link(connection: pymysql.Connection, link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 이미지 url 추출
    imageUrl_tag = soup.find('img', class_='portrait')
    imageUrl = imageUrl_tag['src']
    print(imageUrl)

    # 지역 추출 => but 그냥 string임 어케 id로 match? => split하고 뒷부분이랑 name이랑 매치
    # ex) 남구 야음장생포동 / 화성시 동탄6동
    area = soup.find('div', id='region-name').text
    area_id = find_area(connection, area)
    print(area_id)

    # 제목 추출
    title = soup.find('h1', id='article-title').text
    print(title)

    # 카테고리 추출 => 마찬가지로 그냥 string인데 어떻게 match? => string 값으로 매치?,,,
    # ex) 스포츠/레저 / 남성패션/잡화
    category = soup.find('p', id='article-category').text
    category_id = find_category_dang(category)
    print(category_id)

    # 가격 추출
    price_tag = soup.find('p', id='article-price')
    price = price_tag['content']
    print(price)

    # 내용 추출
    content = soup.find('div', id='article-detail').text
    print(content)

    return {
        'imageUrl': imageUrl,
        'area': area_id,
        'title': title,
        'category': category_id,
        'price': price,
        'content': content
    }
