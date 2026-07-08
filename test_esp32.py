from esp32 import ESP32Controller
import time

esp = ESP32Controller(port="COM3")

print("Waiting...")
time.sleep(2)

print("GREEN")
esp.update(False)

time.sleep(5)

print("RED")
esp.update(True)

time.sleep(5)

print("GREEN")
esp.update(False)

esp.close()