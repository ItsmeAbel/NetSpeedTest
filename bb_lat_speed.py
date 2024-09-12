import speedtest
import matplotlib.pyplot as plt
import subprocess
import time
import os
import numpy as np

def ping_latency(host='8.8.8.8', count=1):
    """Attempt to ping and return latency or None if ping fails."""
    try:
        # Determine the correct ping command for the OS
        ping_command = ['ping', '-c', str(count), host] if os.name != 'nt' else ['ping', '-n', str(count), host]
        
        print(f"Running command: {' '.join(ping_command)}")
        
        # Execute the ping command
        result = subprocess.run(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        
        # Debugging output
        print("Ping output:", output)
        
        if result.returncode != 0:
            print("Ping failed, return code:", result.returncode)
            return None
        
        # Parse the output to find the latency
        if 'time=' in output:
            latency_line = output.split('time=')[-1].strip()
            latency_value = latency_line.split('ms')[0].strip()  # Remove 'ms' and extra spaces
            latency = float(latency_value)  # Extract the time in ms
            return latency
        else:
            print("Ping failed to retrieve latency")
            return None
    except Exception as e:
        print(f"Ping command failed: {e}")
        return None

def measure_network():
    """Measure download and upload speeds using speedtest-cli."""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()  # Automatically pick the best server
        download_speed = st.download() / 1_000_000  # Convert from bps to Mbps
        upload_speed = st.upload() / 1_000_000      # Convert from bps to Mbps
        return download_speed, upload_speed
    except Exception as e:
        print(f"Error during speed test: {e}")
        return None, None

# Lists to store data
download_speeds = []
upload_speeds = []
latencies_before = []
latencies_during = []
latencies_after = []
timestamps = []
Grade = []

# Parameters
num_measurements = 5  # Number of tests
interval = 5          # Time between each test in seconds

for i in range(num_measurements):
    # Measure latency before the speed test
    latency_before = ping_latency()
    latencies_before.append(latency_before)
    if latency_before is not None:
        print(f"Latency before test {i+1}: {latency_before:.2f} ms")
    else:
        print(f"Latency before test {i+1}: Ping failed")

    # Measure download and upload speeds (this causes network load)
    download, upload = measure_network()
    if download is not None and upload is not None:
        download_speeds.append(download)
        upload_speeds.append(upload)
        timestamps.append(time.strftime('%H:%M:%S'))
        print(f"Measurement {i+1} - Download: {download:.2f} Mbps, Upload: {upload:.2f} Mbps")
    else:
        download_speeds.append(None)
        upload_speeds.append(None)

    # Measure latency during the speed test (while network is under load)
    latency_during = ping_latency()
    latencies_during.append(latency_during)
    if latency_during is not None:
        print(f"Latency during test {i+1}: {latency_during:.2f} ms")
        if isinstance(latency_before, (int, float)) and isinstance(latency_during, (int, float)):
            latcalc = latency_during - latency_before
            #latcalc = float(latency_during) - float(latencies_before)
            if latcalc <= 5:
                Grade.append("S")
            elif latcalc <= 30:
                Grade.append("A")
            elif latcalc <= 60:
                Grade.append("B")
            elif latcalc <= 200:
                Grade.append("C")
            elif latcalc <= 400:
                Grade.append("D")
            elif latcalc > 400:
                Grade.append("F")
        else:
            Grade.append("N/A")
    else:
        print(f"Latency during test {i+1}: Ping failed")
        Grade.append('N/A')

    # Wait before next test
    time.sleep(interval)

    # Measure latency after the speed test
    latency_after = ping_latency()
    latencies_after.append(latency_after)
    if latency_after is not None:
        print(f"Latency after test {i+1}: {latency_after:.2f} ms")
    else:
        print(f"Latency after test {i+1}: Ping failed")


def table():
    arrays = [np.array(timestamps), np.array(download_speeds), np.array(upload_speeds),
          np.array(latencies_before), np.array(latencies_during), np.array(latencies_after), np.array(Grade)]
    rows = ['Time','DS', 'US', 'Lpre', 'Lmid', 'Laft', 'Bufferbloat']
    columns = ['Test 1', 'Test 2', 'Test 3', 'Test 4', 'Test 5']

    # Convert arrays to a 2D array
    data = np.vstack(arrays)

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(14,9))

    # Hide the axes
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_frame_on(False)

    # Create a table
    table = ax.table(cellText=data, colLabels=columns, rowLabels=rows, cellLoc='center', loc='center')

    # Adjust the layout
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.2)

def graph():
    # Plotting the results
    plt.figure(figsize=(12, 6))

    # Plot Download and Upload Speeds
    plt.subplot(2, 1, 1)
    plt.plot(timestamps, download_speeds, label='Download Speed (Mbps)', marker='o', color='blue')
    plt.plot(timestamps, upload_speeds, label='Upload Speed (Mbps)', marker='o', color='green')
    plt.ylabel('Speed (Mbps)')
    plt.title('Network Performance: Speed and Latency')
    plt.legend()

    # Plot Latency Before, During, and After Tests
    plt.subplot(2, 1, 2)
    plt.plot(timestamps, latencies_before, label='Latency Before (ms)', marker='x', color='orange')
    plt.plot(timestamps, latencies_during, label='Latency During (ms)', marker='x', color='red')
    plt.plot(timestamps, latencies_after, label='Latency After (ms)', marker='x', color='purple')
    plt.xlabel('Time')
    plt.ylabel('Latency (ms)')
    plt.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()

table()
graph()
plt.show()
