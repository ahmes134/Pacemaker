import serial
import time

class SerialCommunication:
    def __init__(self, port, baudrate=9600, timeout=1):
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
    # Example usage
    pacemaker_serial = SerialCommunication(port='COM3', baudrate=9600)

    try:
        pacemaker_serial.connect()
        
        # Example of sending a command
        pacemaker_serial.send_data("START\n")
        
        # Example of receiving a response
        response = pacemaker_serial.receive_data()
        print(f"Response from pacemaker: {response}")

    finally:
        pacemaker_serial.disconnect()
