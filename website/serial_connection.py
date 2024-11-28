import serial
import threading
import time
import struct
import json

class SerialCommunication:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None

        # Move mode_map to the class level
        self.mode_map = {
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

    def sendSerial(self, mode, LRL, URL, Max_Sensor_Rate, AV_Delay, A_Amplitude, V_Amplitude, A_Pulse_Width, V_Pulse_Width, A_Sensitivity, V_Sensitivity, VRP, ARP, PVARP, Activity_Threshold, Reaction_Time, Response_Factor, Recovery_Time, port):
        """
        Sends formatted serial data to the pacemaker device.
        """
        print("Preparing to send data...")

        # Define the structure for the binary data
        st = struct.Struct('<BBBBBddBBddHHBBdBBBB')

        self.mode_map = {
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

        #activity_threshold_map
        self.activity_threshold_map = {
            'V-Low': 0,
            'Low': 1,
            'Med-Low': 2,
            'Med': 3,
            'Med-High': 4,
            'High': 5,
            'V-High': 6
        }
        

         # Retrieve mode value from the map
        if mode not in self.mode_map:
            print(f"Error: Invalid mode '{mode}'.")
            return

        mode_value = self.mode_map[mode]
        print(f"Using mode: {mode} ({mode_value})")

        if Activity_Threshold not in self.activity_threshold_map:
            print(f"Error: Invalid Activity Threshold '{Activity_Threshold}'.")
            return
        activity_threshold_value = self.activity_threshold_map[Activity_Threshold]
        print(f"Using Activity Threshold: {Activity_Threshold} ({activity_threshold_value})")

        
        def safe_int(value, default=0):
            """
            Safely parse an integer value from the input.
            If parsing fails or the value is 'Off', return the default.
            """
            try:
                if value == 'Off':  # Handle 'Off' case explicitly
                    return 0
                elif value == 'On':  # Handle 'On' case explicitly
                    return 1
                return int(value)
            except (ValueError, TypeError):
                return default
            

        # Ensure values are properly converted and sanitized
        try:
            LRL = safe_int(LRL)
            URL = safe_int(URL)
            Max_Sensor_Rate = safe_int(Max_Sensor_Rate)
            AV_Delay = safe_int(AV_Delay)
            A_Pulse_Width = safe_int(A_Pulse_Width)
            V_Pulse_Width = safe_int(V_Pulse_Width)
            PVARP = safe_int(PVARP)
            Reaction_Time = safe_int(Reaction_Time)
            Response_Factor = safe_int(Response_Factor)
            Recovery_Time = safe_int(Recovery_Time)
            A_Amplitude =  safe_int(A_Amplitude)
            V_Amplitude =  safe_int(V_Amplitude)
            A_Pulse_Width = safe_int(A_Pulse_Width)
            V_Pulse_Width = safe_int(V_Pulse_Width)
            A_Sensitivity = safe_int(A_Sensitivity)
            V_Sensitivity = safe_int(V_Sensitivity)

        except ValueError as e:
            print(f"Error converting values: {e}")
            return

        # Pack data into binary format
        try:
            serial_com = st.pack(
                mode_value, LRL, URL, Max_Sensor_Rate, AV_Delay, A_Amplitude, V_Amplitude, A_Pulse_Width, V_Pulse_Width,
                A_Sensitivity, V_Sensitivity, VRP, ARP, PVARP, activity_threshold_value, Reaction_Time,
                Response_Factor, Recovery_Time, 0, 0
            )

            # Log the parameters being sent
            print("\nTransmitting the following parameters:")
            print(
                f"Mode: {mode_value}, LRL: {LRL}, URL: {URL}, Max Sensor Rate: {Max_Sensor_Rate}")
            print(
                f"AV Delay: {AV_Delay}, Atrial Amplitude: {A_Amplitude}, Ventricular Amplitude: {V_Amplitude}")
            print(
                f"Atrial Pulse Width: {A_Pulse_Width}, Ventricular Pulse Width: {V_Pulse_Width}")
            print(
                f"Atrial Sensitivity: {A_Sensitivity}, Ventricular Sensitivity: {V_Sensitivity}")
            print(f"VRP: {VRP}, ARP: {ARP}, PVARP: {PVARP}")
            print(
                f" Activity Threshold: {activity_threshold_value}")
            print(
                f"Reaction Time: {Reaction_Time}, Response Factor: {Response_Factor}, Recovery Time: {Recovery_Time}")
            print(
                f"A_Pulse_Width: {A_Pulse_Width}, V_Pulse_Width: {V_Pulse_Width}")

            # Send data to the pacemaker
            try:
                uC = serial.Serial(port, baudrate=115200, timeout=1)
                uC.write(serial_com)
                print("Data successfully transmitted.")
                uC.close()
            except serial.SerialException as e:
                print(f"Serial port error: {e}")

        except struct.error as e:
            print(f"Error in struct packing: {e}")

            print(f"Mode: {mode_value} (Type: {type(mode_value)})")
            
        except Exception as e:
            print(f"Error in transmitting data: {e}")


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
        serial_conn = SerialCommunication(port="/dev/cu.usbmodem21103")  # Replace with the actual port
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
