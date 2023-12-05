from dataclasses import dataclass

"""
    상품 정보를 담는 객체

    product_id: 상품 아이디
    product_title: 상품 제목(ex. 로션 팔아요)
    product_content: 상품 설명(게시글 내용)
"""

@dataclass
class Product:

    product_id: int
    product_title: str
    product_content: str

    def to_dict(self) -> dict:
        return {
            'product_id': self.product_id,
            'product_title': self.product_title,
            'product_content': self.product_content
        }
