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

    # 카테고리 정보는 결정난 상태이므로 바로 할당
    category_id = find_category_jung(categoryNum)

    market_name = '중고나라'

    url = 'https://web.joongna.com/search?category=' + categoryNum + '&page=1'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_warpper = soup.find(
        'ul', class_='grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5 gap-x-3 lg:gap-x-5 xl:gap-x-7 gap-y-3 xl:gap-y-5 2xl:gap-y-8 search-results')

    if product_warpper == None:
        return

    articles = product_warpper.find_all('a')

    for article in articles[:3]:
        link = article['href']

        # 중간에 섞여있는 광고 스킵
        if (link.split('/')[1] != 'product'):
            continue

        # 마켓 ID 추출 후 데이터 추출을 위해 링크 재할당
        market_product_id = link.split('/')[-1]
        link = 'https://web.joongna.com' + link

        # DB에서 market_product_id 조회 후 중복시 해당 루프 스킵
        if (is_market_product_id_onDB(connection, market_product_id)):
            print('Skip this product : Already on DB => ' +
                  market_product_id + '\n\n')
            continue

        # 지역 추출
        raw_area = article.find('span', class_='text-sm text-gray-400').text
        if raw_area == '':
            area = '불명'
            print('Skip this product : No area Info in DB => ' + area + '\n\n')
            continue
        else:
            area = raw_area.split()[-1]
            area_id = find_area(connection, area)

        if area_id == 0:
            print('Skip this product : No area Info in DB => ' + area + '\n\n')
            continue

        product_info = get_product_info(link)
        product_info['area'] = area_id
        product_info['category'] = category_id
        product_info['product_link'] = link

        # 데이터 종합해서 product 생성
        product = create_product(
            product_info, market_product_id, market_name)
        print('Successfully Created')

        print(product)

        # DB에 product 생성
        save_product(connection, product)
        print("Successfully Saved" + '\n\n')


def get_product_info(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    img_tag = soup.find('meta', property='og:image')
    imageUrl = img_tag['content']

    title_tag = soup.find('meta', property='og:title')
    title = title_tag['content']

    price_info = soup.find(
        'div', class_='text-heading font-bold text-[40px] pe-2 md:pe-0 lg:pe-2 2xl:pe-0 mr-2').text
    price_info = price_info[:-1]
    price = int(price_info.replace(',', ''))

    content = soup.find(
        'p', class_='px-4 py-10 break-words break-all whitespace-pre-line lg:py-2').text

    return {
        'imageUrl': imageUrl,
        'title': title,
        'price': price,
        'content': content
    }
