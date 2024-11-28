import serial
import threading
import time
import struct


class SerialCommunication:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None

    def connect(self):
        try:
            self.serial_conn = serial.Serial(
                port=self.port, baudrate=self.baudrate, timeout=self.timeout)
            print(f"Connected to {self.port} at {self.baudrate} baudrate.")
        except serial.SerialException as e:
            print(f"Connection failed: {e}")

    def disconnect(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            print("Serial connection closed.")

    def is_connected(self):
        if self.serial_conn and self.serial_conn.is_open:
            try:
                # Non-intrusive check for connection
                self.serial_conn.in_waiting  # Check if the port is responsive
                return True
            except (serial.SerialException, OSError):
                self.serial_conn.close()
                self.serial_conn = None
        return False

    def sendSerial(self, mode, LRL, URL, Max_Sensor_Rate, AV_Delay, A_Amplitude, V_Amplitude, A_Pulse_Width, V_Pulse_Width, A_Sensitivity, V_Sensitivity, VRP, ARP, PVARP, Rate_Smoothing, Activity_Threshold, Reaction_Time, Response_Factor, Recovery_Time, Function_Call, port):
        """
        Sends formatted serial data to the pacemaker device.
        """
        print("sending data")
        # Define the structure for the binary data
        st = struct.Struct('<BBBBBddBBddHHBBdBBBB')

        # Mapping for modes
        mode_map = {
            'AOO': 1,
            'VOO': 2,
            'AAI': 3,
            'VVI': 4,
            'DOO': 5,
            'AOOR': 6,
            'VOOR': 7,
            'AAIR': 8,
            'VVIR': 9,
            'DOOR': 10
        }

        try:
            mode_value = mode_map[mode]
        except KeyError:
            print(f"Error: Invalid mode '{mode}'.")
            return

        # Ensure values are properly converted and sanitized
        LRL = int(LRL)
        URL = int(URL)
        Max_Sensor_Rate = int(Max_Sensor_Rate)
        AV_Delay = int(AV_Delay)
        A_Pulse_Width = int(A_Pulse_Width)
        V_Pulse_Width = int(V_Pulse_Width)
        PVARP = int(PVARP)
        Rate_Smoothing = int(Rate_Smoothing)
        Reaction_Time = int(Reaction_Time)
        Response_Factor = int(Response_Factor)
        Recovery_Time = int(Recovery_Time)
        Function_Call = int(Function_Call)

        # Pack data into binary format
        try:
            serial_com = st.pack(
                mode_value, LRL, URL, Max_Sensor_Rate, AV_Delay, A_Amplitude, V_Amplitude, A_Pulse_Width, V_Pulse_Width,
                A_Sensitivity, V_Sensitivity, VRP, ARP, PVARP, Rate_Smoothing, Activity_Threshold, Reaction_Time,
                Response_Factor, Recovery_Time, Function_Call
            )

            # Log the parameters being sent
            print("\nTransmitting the following parameters:")
            print(
                f"Mode: {mode}, LRL: {LRL}, URL: {URL}, Max Sensor Rate: {Max_Sensor_Rate}")
            print(
                f"AV Delay: {AV_Delay}, Atrial Amplitude: {A_Amplitude}, Ventricular Amplitude: {V_Amplitude}")
            print(
                f"Atrial Pulse Width: {A_Pulse_Width}, Ventricular Pulse Width: {V_Pulse_Width}")
            print(
                f"Atrial Sensitivity: {A_Sensitivity}, Ventricular Sensitivity: {V_Sensitivity}")
            print(f"VRP: {VRP}, ARP: {ARP}, PVARP: {PVARP}")
            print(
                f"Rate Smoothing: {Rate_Smoothing}, Activity Threshold: {Activity_Threshold}")
            print(
                f"Reaction Time: {Reaction_Time}, Response Factor: {Response_Factor}, Recovery Time: {Recovery_Time}")
            print(f"Function Call: {Function_Call}, Port: {port}")

            # Send data to the pacemaker
            uC = serial.Serial(port, baudrate=115200)
            uC.write(serial_com)
            print("Data successfully transmitted.")
            uC.close()

        except Exception as e:
            print(f"Error in transmitting data: {e}")

    def send_data(self, data):
        """
        Sends raw string data to the pacemaker.
        """
        if self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(data.encode())
                print(f"Sent data: {data}")
            except Exception as e:
                print(f"Failed to send data: {e}")

    def receive_data(self):
        """
        Receives data from the pacemaker.
        """
        if self.serial_conn and self.serial_conn.is_open:
            try:
                received = self.serial_conn.readline().decode().strip()
                print(f"Received data: {received}")
                return received
            except serial.SerialException:
                print("Error reading from serial port.")
        return None


# Instantiate the SerialCommunication class
serial_conn = SerialCommunication(port="COM11")  # Replace with the actual port
serial_conn.connect()

# Shared resource with thread safety
connection_status = {"pacemaker_status": "Out of Range",
                     "pacemaker_status_class": "out-of-range"}
status_lock = threading.Lock()

# Event to signal the polling thread to stop
stop_event = threading.Event()


def poll_connection_status():
    """
    Continuously checks the pacemaker's connection status.
    """
    global connection_status
    while not stop_event.is_set():
        is_connected = serial_conn.is_connected()
        with status_lock:
            previous_status = connection_status["pacemaker_status"]
            connection_status = {
                "pacemaker_status": "Connected" if is_connected else "Out of Range",
                "pacemaker_status_class": "connected" if is_connected else "out-of-range"
            }
            if connection_status["pacemaker_status"] != previous_status:
                print(
                    f"Connection status changed to: {connection_status['pacemaker_status']}")


# Start the polling thread
polling_thread = threading.Thread(target=poll_connection_status, daemon=True)
polling_thread.start()


def get_connection_status():
    """
    Safely retrieve the current connection status.
    Returns:
        dict: The current connection status.
    """
    with status_lock:
        return connection_status


if __name__ == "__main__":
    try:
        while True:
            # Print the current connection status
            print(get_connection_status())
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping...")
        stop_event.set()
        polling_thread.join()
        serial_conn.disconnect()
        print("Exited.")
