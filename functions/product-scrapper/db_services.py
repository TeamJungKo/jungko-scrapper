import pymysql
import datetime


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


def find_category_bun(categoryNum):

    # 여성의류
    if categoryNum == '310300':
        return 3
    elif categoryNum == '310260':
        return 4
    elif categoryNum == '310150':
        return 5
    elif categoryNum == '310130':
        return 6
    elif categoryNum == '310120':
        return 7
    elif categoryNum == '310250':
        return 9
    elif categoryNum == '310400':
        return 9
    elif categoryNum == '310200':
        return 8
    elif categoryNum == '310220':
        return 9

    # 남성의류
    elif categoryNum == '320300':
        return 11
    elif categoryNum == '320210':
        return 12
    elif categoryNum == '320120':
        return 13
    elif categoryNum == '320400':
        return 16
    elif categoryNum == '320500':
        return 14
    elif categoryNum == '320160':
        return 15
    elif categoryNum == '320180':
        return 16

    # 신발
    elif categoryNum == '405100':
        return 21
    elif categoryNum == '405300':
        return 19
    elif categoryNum == '405200':
        return 18
    elif categoryNum == '405400':
        return 20

    # 가방/지갑
    elif categoryNum == '430100':
        return 23
    elif categoryNum == '430200':
        return 24
    elif categoryNum == '430300':
        return 25
    elif categoryNum == '430400':
        return 26
    elif categoryNum == '430500':
        return 27
    elif categoryNum == '430999':
        return 28

    # 시계
    # '421200', '421100', '421300',
    elif categoryNum == '421200':
        return 30
    elif categoryNum == '421100':
        return 31
    elif categoryNum == '421309':
        return 32

    # 쥬얼리
    elif categoryNum == '422200':
        return 35
    elif categoryNum == '422100':
        return 36
    elif categoryNum == '422300':
        return 37
    elif categoryNum == '422400':
        return 37
    elif categoryNum == '422500':
        return 38
    elif categoryNum == '422600':
        return 39
    elif categoryNum == '422999':
        return 39

    # 패션 악세서리
    elif categoryNum == '400070':
        return 41
    elif categoryNum == '400080':
        return 42
    elif categoryNum == '400120':
        return 43
    elif categoryNum == '400130':
        return 44
    elif categoryNum == '400110':
        return 45
    elif categoryNum == '400140':
        return 46
    elif categoryNum == '400090':
        return 47
    elif categoryNum == '400600':
        return 48
    elif categoryNum == '400999':
        return 48

    # 디지털
    elif categoryNum == '600700':
        return 50
    elif categoryNum == '600710':
        return 51
    elif categoryNum == '600720':
        return 52
    elif categoryNum == '600500':
        return 87
    elif categoryNum == '600100':
        return 57
    elif categoryNum == '600600':
        return 69
    elif categoryNum == '600300':
        return 71
    elif categoryNum == '600200':
        return 57

    # 가전제품
    elif categoryNum == '610500':
        return 89
    elif categoryNum == '610600':
        return 85
    elif categoryNum == '610700':
        return 90
    elif categoryNum == '610200':
        return 85
    elif categoryNum == '610400':
        return 88
    elif categoryNum == '610300':
        return 84
    elif categoryNum == '610100':
        return 83
    elif categoryNum == '610800':
        return 91
    elif categoryNum == '610999':
        return 92

    # 스포츠/레저
    elif categoryNum == '700600':
        return 188
    elif categoryNum == '700200':
        return 203
    elif categoryNum == '700250':
        return 204
    elif categoryNum == '700110':
        return 189
    elif categoryNum == '700120':
        return 190
    elif categoryNum == '700130':
        return 191
    elif categoryNum == '700350':
        return 192
    elif categoryNum == '700700':
        return 193
    elif categoryNum == '700650':
        return 194
    elif categoryNum == '700500':
        return 195
    elif categoryNum == '700400':
        return 196
    elif categoryNum == '700150':
        return 197
    elif categoryNum == '700140':
        return 197
    elif categoryNum == '700160':
        return 198
    elif categoryNum == '700170':
        return 198
    elif categoryNum == '700180':
        return 198
    elif categoryNum == '700900':
        return 199
    elif categoryNum == '700800':
        return 200
    elif categoryNum == '700810':
        return 201
    elif categoryNum == '700950':
        return 202

    # 차량/오토바이
    elif categoryNum == '750200':
        return 208
    elif categoryNum == '750100':
        return 209
    elif categoryNum == '750610':
        return 210
    elif categoryNum == '750800':
        return 211
    elif categoryNum == '750810':
        return 212
    elif categoryNum == '750910':
        return 213

    # 스타굿즈
    elif categoryNum == '910100':
        return 180
    elif categoryNum == '910200':
        return 181
    elif categoryNum == '910500':
        return 182
    elif categoryNum == '910400':
        return 183
    elif categoryNum == '910600':
        return 184
    elif categoryNum == '910700':
        return 185
    elif categoryNum == '910800':
        return 186

    # 키덜트
    elif categoryNum == '930100':
        return 94
    elif categoryNum == '930200':
        return 95
    elif categoryNum == '930300':
        return 96
    elif categoryNum == '930500':
        return 97
    elif categoryNum == '930400':
        return 98
    elif categoryNum == '930600':
        return 102
    elif categoryNum == '930999':
        return 102

    # 예술/희귀/수집품
    elif categoryNum == '990100':
        return 104
    elif categoryNum == '990200':
        return 105
    elif categoryNum == '990309':
        return 106

    # 음반/악기
    elif categoryNum == '920100':
        return 113
    elif categoryNum == '920200':
        return 107

    # 도서/티켓/문구
    elif categoryNum == '900100':
        return 112
    elif categoryNum == '900500':
        return 114
    elif categoryNum == '900220':
        return 117
    elif categoryNum == '900230':
        return 117
    elif categoryNum == '900219':
        return 116

    # 뷰티/미용
    elif categoryNum == '410100':
        return 121
    elif categoryNum == '410400':
        return 122
    elif categoryNum == '410300':
        return 123
    elif categoryNum == '410600':
        return 124
    elif categoryNum == '410500':
        return 125
    elif categoryNum == '410700':
        return 126
    elif categoryNum == '410800':
        return 127
    elif categoryNum == '410900':
        return 128
    elif categoryNum == '410950':
        return 129

    # 가구 인테리어
    elif categoryNum == '810100':
        return 130
    elif categoryNum == '810901':
        return 132
    elif categoryNum == '810300':
        return 135
    elif categoryNum == '810902':
        return 139
    elif categoryNum == '810400':
        return 140
    elif categoryNum == '810500':
        return 142
    elif categoryNum == '810903':
        return 136
    elif categoryNum == '810904':
        return 137
    elif categoryNum == '810905':
        return 138

    # 생활/주방용품
    elif categoryNum == '800400':
        return 144
    elif categoryNum == '800600':
        return 145
    elif categoryNum == '800100':
        return 146

    # 공구/산업용품
    elif categoryNum == '830100':
        return 148
    elif categoryNum == '830200':
        return 149
    elif categoryNum == '830300':
        return 150
    elif categoryNum == '830700':
        return 151
    elif categoryNum == '830600':
        return 152
    elif categoryNum == '830500':
        return 153
    elif categoryNum == '830400':
        return 154
    elif categoryNum == '830999':
        return 155

    # 식품
    elif categoryNum == '820100':
        return 165
    elif categoryNum == '820200':
        return 158
    elif categoryNum == '820300':
        return 159
    elif categoryNum == '820700':
        return 160
    elif categoryNum == '820600':
        return 161
    elif categoryNum == '820500':
        return 162
    elif categoryNum == '820800':
        return 163
    elif categoryNum == '820400':
        return 164
    elif categoryNum == '820999':
        return 157

    # 유아동/출산
    elif categoryNum == '500110':
        return 169
    elif categoryNum == '500111':
        return 169
    elif categoryNum == '500113':
        return 169
    elif categoryNum == '500114':
        return 169
    elif categoryNum == '500115':
        return 169
    elif categoryNum == '500116':
        return 170
    elif categoryNum == '500117':
        return 168
    elif categoryNum == '500118':
        return 167
    elif categoryNum == '500119':
        return 172
    elif categoryNum == '500120':
        return 167

    # 반려동물용품
    elif categoryNum == '980100':
        return 175
    elif categoryNum == '980200':
        return 175
    elif categoryNum == '980300':
        return 175
    elif categoryNum == '980400':
        return 176
    elif categoryNum == '980500':
        return 176
    elif categoryNum == '980600':
        return 176
    elif categoryNum == '980990':
        return 178
    elif categoryNum == '980999':
        return 178

    else:   # 포함되지 않는 물품들 (부동산, 아르바이트 등)
        return 0
