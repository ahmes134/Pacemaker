import serial

class SerialCommunication:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None

    def connect(self):
        try:
            self.serial_conn = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            print(f"Connected to {self.port} at {self.baudrate} baudrate.")
        except serial.SerialException as e:
            print(f"Connection failed: {e}")

    def disconnect(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Serial connection closed.")

    def is_connected(self):
        if self.serial_conn and self.serial_conn.is_open:
            return True
        try:
            self.connect()
            return self.serial_conn.is_open
        except:
            return False

    def send_data(self, data):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(data.encode())

    def receive_data(self):
        if self.serial_conn and self.serial_conn.is_open:
            return self.serial_conn.readline().decode().strip()
