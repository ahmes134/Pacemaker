import serial
import time

class SerialCommunication:
    def __init__(self, port, baudrate=11520, timeout=1):
        """
        Initialize the serial connection.
        :param port: Serial port (e.g., 'COM3' or '/dev/ttyUSB0')
        :param baudrate: Communication speed
        :param timeout: Timeout for read/write operations
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None

    def connect(self):
        """
        Open the serial connection.
        """
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            print(f"Connected to {self.port} at {self.baudrate} baudrate.")
        except serial.SerialException as e:
            print(f"Failed to connect to {self.port}: {e}")

    def disconnect(self):
        """
        Close the serial connection.
        """
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Serial connection closed.")

    def is_connected(self):
        """
        Check if the serial connection is active.
        :return: True if connected, False otherwise.
        """
        return self.serial_conn is not None and self.serial_conn.is_open

    def send_data(self, data):
        """
        Transmit data to the pacemaker.
        :param data: Data to send (string or bytes)
        """
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(data.encode('utf-8') + b'\n')
                print(f"Sent: {data}")
            except serial.SerialTimeoutException as e:
                print(f"Failed to send data: {e}")
        else:
            print("Serial connection is not open.")

    def receive_data(self):
        """
        Receive data from the pacemaker.
        :return: Received data (string)
        """
        if self.serial_conn and self.serial_conn.is_open:
            try:
                received = self.serial_conn.readline().decode('utf-8').strip()
                print(f"Received: {received}")
                return received
            except serial.SerialException as e:
                print(f"Failed to receive data: {e}")
                return None
        else:
            print("Serial connection is not open.")
            return None

if __name__ == "__main__":

    port = "COM11"  # Replace with your port
    baudrate = 11520
    timeout = 1

    try:
        # Attempt to open the connection
        conn = serial.Serial(port, baudrate, timeout=timeout)
        if conn.is_open:
            print(f"Successfully connected to {port}")
        conn.close()
    except serial.SerialException as e:
        print(f"SerialException: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
