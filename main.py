import serial
from datetime import datetime
import os
import serial.tools.list_ports


# List all available COM ports
ports = serial.tools.list_ports.comports()
port_dict = {}

print("Available COM ports:")
for i, port in enumerate(ports):
  port_dict[i] = port.device
  print(f"- [{i}] {port.device}")

# Prompt the user to select a COM port
selected_port = None
while True:
  try:
    selected_index = int(input("Enter the port number to connect: "))
    selected_port = port_dict[selected_index]
    print("\033[92mSelected port:", selected_port, "\033[0m")
    # Open the selected serial port
    ser = serial.Serial(selected_port, 921600, parity=serial.PARITY_EVEN, timeout=5)
    break
  except (ValueError, KeyError):
    print("\033[91mInvalid port number. Please try again.\033[0m")
  except serial.SerialException:
    print("\033[91mFailed to open the selected port. Please try again.\033[0m")

def convert_fgm(data):
  data_int = 0
  for i in range(1, 6):
    data_int += (data[i] - 0x30) * 10 ** (5 - i)
  data_int = data_int * 10 / 32767
  result = bytes([data[0]])
  return result.decode('ascii') + f'{data_int:.3f}V'

# Read data from the serial port
data = b''  # Initialize an empty byte string
while True:
  data += ser.read()  # Read a single byte from the serial port and append it to the data

  count = 0  # Initialize a counter variable

  while True:
    data += ser.read()  # Read a single byte from the serial port and append it to the data

    if len(data) >= 50:
      # Split the data into 6-byte ADC data chunks
      adc_data = [data[i:i+6] for i in range(0, 36, 6)]
      print(adc_data)

      # Convert the ADC data to voltage
      voltage_data = [convert_fgm(data) for data in adc_data]
      print(voltage_data)

      # Reset the data variable
      data = b''

      # Write voltage data to data.txt
      file_name = datetime.now().strftime("%Y%m%d") + '.txt'
      current_time = datetime.now().strftime("%H:%M:%S.%f")[:-4]
      folder_path = './data/'
      if not os.path.exists(folder_path):
        os.makedirs(folder_path)
      with open(os.path.join(folder_path, file_name), 'a') as file:
        file.write(current_time + ' ')
        for voltage in voltage_data:
          file.write(voltage + ' ')
        file.write('\n')

      # Clear the terminal screen every 200 data points
      count += 1
      if count % 200 == 0:
        count = 0
        os.system('cls' if os.name == 'nt' else 'clear')
