import os
import base64
import json
import firebase_admin
from firebase_admin import credentials, messaging
from models import Notification

firebase_credential = os.getenv('FIREBASE_CREDENTIALS')
default_image_url = os.getenv('DEFAULT_IMAGE_URL')
base_url = os.getenv('BASE_URL')


def send_notification(notifications: list[Notification]):
    base64_decoded_firebase_credential = base64.b64decode(firebase_credential)
    firebase_credential_json = json.loads(base64_decoded_firebase_credential)
    cred = credentials.Certificate(firebase_credential_json)
    default_app = firebase_admin.initialize_app(cred)

    messages = [
        messaging.Message(
            notification=messaging.Notification(
                title=notification.notice_title,
                body=notification.notice_content,
                image=default_image_url
            ),
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    icon=default_image_url,
                    actions=[
                        messaging.WebpushNotificationAction(
                            action='view_product',
                            title='상품 보기',
                            icon=default_image_url
                        )
                    ],
                    image=default_image_url,
                    data={
                        'url': f"{base_url}/product/{notification.product_id}"
                    },
                ),
            ),
            token=notification.device_token,
        )
        for notification in notifications
    ]

    response = messaging.send_all(messages)
    firebase_admin.delete_app(default_app)

    print(response.success_count, 'tokens were subscribed successfully')
    print(response.failure_count, 'tokens were not subscribed')
