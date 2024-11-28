import serial
import struct
from time import sleep
from serial.tools.list_ports import comports
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Initialize lists to store the data
time_values = []  # For x-axis (time)
aSignal_values = []  # Atrium signal values
vSignal_values = []  # Ventricle signal values
time_step = 0.1  # Time step between readings

# Select the COM port dynamically
print("Available COM ports:")
for port in comports():
    print(port)

# Initialize the serial connection
with serial.Serial(port="COM11", baudrate=115200) as ser:
    ser.timeout = 1  # Set timeout for reading

    def read_serial_data():
        """Read atrium and ventricle signals from the serial port."""
        global time_values, aSignal_values, vSignal_values
        ser.write(b"\x16\x47" + b"\x00" * 50)  # Write command
        sleep(0.1)
        data_r = ser.read(50)  # Read 50 bytes from the serial buffer

        # Unpack the received data for aSignal and vSignal
        if len(data_r) >= 16:  # Ensure we have enough data
            try:
                aSignal = struct.unpack("d", data_r[0:8])[0] * 3.3
                vSignal = struct.unpack("d", data_r[8:16])[0] * 3.3
                return aSignal, vSignal
            except struct.error:
                print("Error unpacking data.")
                return None, None
        return None, None

    # Function to update the graph
    def update_graph(frame):
        global time_values, aSignal_values, vSignal_values

        # Read the next set of data
        aSignal, vSignal = read_serial_data()
        if aSignal is not None and vSignal is not None:
            # Update time and signal values
            if len(time_values) == 0:
                current_time = 0
            else:
                current_time = time_values[-1] + time_step
            time_values.append(current_time)
            aSignal_values.append(aSignal)
            vSignal_values.append(vSignal)

            # Keep only the last 50 points (optional, for real-time performance)
            if len(time_values) > 50:
                time_values = time_values[-50:]
                aSignal_values = aSignal_values[-50:]
                vSignal_values = vSignal_values[-50:]

            # Update the plots
            atrial_line.set_data(time_values, aSignal_values)
            ventricular_line.set_data(time_values, vSignal_values)

            # Adjust x-axis dynamically
            ax.set_xlim(max(0, current_time - 5), current_time + 1)
            ax.set_ylim(min(min(aSignal_values), min(vSignal_values)) - 0.5,
                        max(max(aSignal_values), max(vSignal_values)) + 0.5)
        return atrial_line, ventricular_line

    # Set up the plot
    fig, ax = plt.subplots()
    atrial_line, = ax.plot([], [], label="Atrium Signal (V)", color="blue")
    ventricular_line, = ax.plot(
        [], [], label="Ventricle Signal (V)", color="red")
    ax.set_title("Live Egram Monitoring")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    ax.legend()
    ax.grid()

    # Animate the graph
    ani = FuncAnimation(fig, update_graph, interval=100)  # Update every 100ms
    plt.show()

    # Stop monitoring and close the serial connection
    ser.write(b"\x16\x62" + b"\x00" * 50)
    sleep(0.1)
    ser.write(b"\x16\x22" + b"\x00" * 50)
    ser.close()
