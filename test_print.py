import serial
import time

# Micro:bitが接続されているシリアルポートを指定
SERIAL_PORT = '/dev/tty.usbmodem114302'  # Macの場合（Windowsでは COMx）
BAUD_RATE = 115200  # Micro:bitのボーレート

# シリアルポートを開く
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

while True:
    try:
        # シリアルポートからデータを読み取る
        line = ser.readline().decode('utf-8').strip()  # デコードして改行を削除
        print(f"Current temperature: {line} °C")  # 温度を表示
        time.sleep(1)  # 1秒ごとに更新
    except Exception as e:
        print(f"Error: {e}")
        break
