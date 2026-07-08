import serial
import time


class ESP32Controller:

    def __init__(self, port="COM3", baudrate=115200):

        print(f"Connecting to ESP32 on {port}...")

        self.serial = serial.Serial(port, baudrate, timeout=1)

        # Wait for ESP32 to reboot
        time.sleep(3)

        # Clear buffers
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

        self.last_status = None

        print("✅ Connected to ESP32")

    def update(self, crack_detected):

        if crack_detected:

            if self.last_status != "RED":

                print("Sending -> RED")

                self.serial.write(b"RED\n")
                self.serial.flush()

                self.last_status = "RED"

        else:

            if self.last_status != "GREEN":

                print("Sending -> GREEN")

                self.serial.write(b"GREEN\n")
                self.serial.flush()

                self.last_status = "GREEN"

    def close(self):

        if self.serial.is_open:
            self.serial.close()