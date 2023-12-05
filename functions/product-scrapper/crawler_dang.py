import requests
from bs4 import BeautifulSoup
import pymysql
from db_services import find_area, find_category_dang, is_market_product_id_onDB, create_product, save_product_list


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

    product_list = []
    for article in articles:
        try:
            a_tag = article.find('a')
            if a_tag and 'href' in a_tag.attrs:
                link = a_tag['href']

                # 추출한 데이터 처리에 market_product_id 추가 => DB에서 string
                market_product_id = link.split('/')[2]
                link = 'https://www.daangn.com' + link

                # DB에서 market_product_id 조회 후 중복시 해당 루프 스킵
                if (is_market_product_id_onDB(connection, market_product_id)):
                    print('Skip this product : Already on DB => ' +
                          market_product_id + '\n\n')
                    continue

                # 링크로 접근하여 데이터 추출
                article_data = extract_data_from_link(connection, link)

                # 데이터 종합해서 product 생성
                product = create_product(
                    article_data, market_product_id, market_name)
                print('Successfully Created')

                # 만약 읍면동 조회 불가라면 해당 루프 스킵
                if (article_data['area'] == 0):
                    print('Skip this product : No area Info in DB' + '\n\n')
                    continue

                # # DB에 product 생성
                # save_product(connection, product)
                # print("Successfully Saved" + '\n\n')
                product_list.append(product)
        except Exception as e:
            print(e)
            continue

    # DB에 product 생성
    save_product_list(connection, product_list)


# hot_articles에 있는 링크를 인자로 받아서 해당 링크에서 데이터 추출
def extract_data_from_link(connection: pymysql.Connection, link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 비밀 게시물 예외 처리
    if soup.find('p', id='no-article'):
        return {'area': 0}

    # 이미지 url 추출
    imageUrl_tag = soup.find('img', class_='portrait')
    if imageUrl_tag == None:
        imageUrl_tag = soup.find('img', class_='landscape')
    imageUrl = imageUrl_tag['src']

    # 지역 추출
    area = soup.find('div', id='region-name').text
    area_list = area.split()
    if len(area_list) == 2:
        area = area_list[1]
    else:
        area = area_list[2]
    area_id = find_area(connection, area)

    # 제목 추출
    title = soup.find('h1', id='article-title').text

    # 카테고리 추출
    category = soup.find('p', id='article-category').text
    category = category.split()[0]
    category_id = find_category_dang(category)

    # 가격 추출
    price_tag = soup.find('p', id='article-price')
    if price_tag is None:
        price = 0
    else:
        price = price_tag['content']

    # 내용 추출
    content = soup.find('div', id='article-detail').text

    return {
        'imageUrl': imageUrl,
        'area': area_id,
        'title': title,
        'category': category_id,
        'price': price,
        'content': content,
        'product_link': link
    }
