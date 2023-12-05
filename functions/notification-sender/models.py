from dataclasses import dataclass

"""
    알림 정보를 담는 객체
    target_member_id: 알림을 받을 회원의 id
    target_member_nickname: 알림을 받을 회원의 닉네임
    target_member_email: 알림을 받을 회원의 이메일
    device_token: 알림을 받을 회원의 디바이스 토큰
    notice_title: 알림 제목 (ex. [${상품 키워드} ${알림 타입} 알림] ${지역})
    notice_content: 알림 내용 (ex. ${상품 제목})
"""


@dataclass
class Notification:
    target_member_id: int
    target_member_nickname: str
    target_member_email: str
    device_token: str
    notice_title: str
    notice_content: str
    product_id: int

    def to_dict(self) -> dict:
        return {
            'target_member_id': self.target_member_id,
            'target_member_nickname': self.target_member_nickname,
            'target_member_email': self.target_member_email,
            'device_token': self.device_token,
            'notice_title': self.notice_title,
            'notice_content': self.notice_content,
            'product_id': self.product_id
        }
