"""GSM service — SMS alerts routed through the ESP32 GSM module."""

from backend.storage.gsm_store import load_phone_number, save_phone_number


class GsmService:
    """Sends SMS alerts via the ESP32 GSM module and persists the operator
    phone number to config/gsm_settings.csv (see backend.storage.gsm_store)."""

    def __init__(self, esp32_controller):
        self._esp = esp32_controller

    def send_sms(self, phone: str, message: str) -> bool:
        return bool(self._esp.send_sms(phone, message))

    def send_test_sms(self) -> bool:
        return bool(self._esp.send_test_sms())

    def get_phone_number(self) -> str | None:
        return load_phone_number()

    def save_phone_number(self, phone: str) -> None:
        save_phone_number(phone)
