import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# 🔑 Твои данные (не выкладывай их публично)
ACCESS_KEY = "0064a4804997f000000000001"
SECRET_KEY = "K006dMLcanB5LogjKrrjKgcgvo7IgYg"
ENDPOINT_URL = "https://s3.ca-east-006.backblazeb2.com"
BUCKET_NAME = "atatek"

# Подключаемся к B2 через S3 API
print("📡 Подключаемся к Backblaze B2...")
s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name="ca-east-006"
)
print("✅ Подключение успешно.\n")


def upload_image(file_path: str, file_name: str) -> str:
    """
    Загружает файл в Backblaze B2 и возвращает публичную ссылку.
    """
    print(f"📤 Начинаем загрузку файла: {file_path}")
    try:
        s3.upload_file(file_path, BUCKET_NAME, file_name)
        print(f"✅ Файл '{file_name}' успешно загружен в bucket '{BUCKET_NAME}'.")
        public_url = f"https://{BUCKET_NAME}.s3.ca-east-006.backblazeb2.com/{file_name}"
        print(f"🔗 Публичная ссылка: {public_url}\n")
        return public_url

    except FileNotFoundError:
        print("❌ Ошибка: файл не найден.")
    except NoCredentialsError:
        print("❌ Ошибка: нет доступа к ключам (ACCESS_KEY / SECRET_KEY).")
    except ClientError as e:
        print("❌ Ошибка клиента AWS S3:", e)
    except Exception as e:
        print("❌ Неизвестная ошибка:", e)


# 🚀 Пример использования
if __name__ == "__main__":
    print("🚀 Тестовая загрузка начата...\n")
    url = upload_image("IMG_4580.JPG", "IMG_4580.JPG")
    if url:
        print("🎉 Всё прошло успешно!")
    else:
        print("⚠️ Что-то пошло не так.")
