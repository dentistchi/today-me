import os
from dotenv import load_dotenv
load_dotenv()

smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')
from_email = os.getenv('FROM_EMAIL')

print('SMTP 설정 확인:')
print(f'SMTP_USER: {"설정됨" if smtp_user else "없음"}')
print(f'SMTP_PASSWORD: {"설정됨" if smtp_password else "없음"}')
print(f'FROM_EMAIL: {from_email if from_email else "SMTP_USER 사용"}')
