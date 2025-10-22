from __future__ import annotations
import secrets
from typing import Optional
from argon2 import PasswordHasher, exceptions as argon2_exceptions

class AuthUtils:
    """
    Утилитный класс для:
      - генерации 6-значного кода (строка, ведущие нули сохраняются)
      - хеширования пароля с использованием Argon2
      - верификации пароля против хеша Argon2

    Использует argon2-cffi (PasswordHasher). По умолчанию параметры безопасны для
    общих случаев, но вы можете передать свои при инициализации.
    """

    def __init__(
        self,
        time_cost: int = 2,
        memory_cost: int = 102400,  # в kibibytes (100 MiB)
        parallelism: int = 8,
        hash_len: int = 32,
        salt_len: int = 16,
    ):
        """
        Аргументы:
          time_cost: итерации (чем больше — тем медленнее/безопаснее)
          memory_cost: количество памяти в KiB
          parallelism: параллелизм (кол-во потоков)
          hash_len: длина результирующего хеша (байт)
          salt_len: длина соли (байт)
        """
        self._ph = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len,
        )

    @staticmethod
    def generate_6_digit_code() -> str:
        """
        Генерирует криптографически-стойкий 6-значный код как строку.
        Всегда возвращает 6 символов (ведущие нули включены).
        """
        n = secrets.randbelow(10**6)  # 0..999999
        return f"{n:06d}"

    def hash_password(self, password: str) -> str:
        """
        Хеширует пароль и возвращает строковый хеш Argon2 (формат, совместимый с PasswordHasher).
        Вход:
          password: чистая строка пароля
        Выход:
          строковый хеш, который можно сохранять в БД
        """
        if not isinstance(password, str):
            raise TypeError("password must be a str")
        if password == "":
            # опционально — можно запретить пустые пароли
            raise ValueError("password must not be empty")
        return self._ph.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Проверяет пароль против хеша.
        Возвращает True если совпадает, False если нет.
        Никаких исключений наружу не пропускает кроме TypeError/ValueError при неверных типах.
        """
        if not isinstance(password, str) or not isinstance(hashed, str):
            raise TypeError("password and hashed must be str")
        try:
            return self._ph.verify(hashed, password)
        except argon2_exceptions.VerifyMismatchError:
            return False
        except argon2_exceptions.VerificationError:
            # прочие ошибки верификации (например повреждённый хеш)
            return False

    def needs_rehash(self, hashed: str) -> bool:
        """
        Опционально: проверка, нужно ли перехешировать старый хеш
        (например, если вы подняли параметры безопасности).
        """
        try:
            return self._ph.check_needs_rehash(hashed)
        except Exception:
            # если хеш некорректен — сигнально вернуть True, чтобы обновить/перехешировать
            return True

