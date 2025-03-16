import serial
import time
from flask import Flask, render_template, jsonify
import threading

# Flask にテンプレートフォルダのパスを指定します。
app = Flask(__name__, template_folder='/Users/yamamototakuma/Desktop/python/発表/programs/html')

# シリアルポートの設定
try:
    ser1 = serial.Serial('/dev/tty.usbmodem14202', baudrate=115200, timeout=1)  # 1台目のMicro:bit
except Exception as e:
    ser1 = None
    print("Error opening Micro:bit 1:", e)

try:
    ser2 = serial.Serial('/dev/tty.usbmodem14302', baudrate=115200, timeout=1)  # 2台目のMicro:bit
except Exception as e:
    ser2 = None
    print("Error opening Micro:bit 2:", e)

# グローバル変数：温度データとエラーメッセージ
temperature1 = None
temperature2 = None
error_message1 = None
error_message2 = None

def read_temperature():
    global temperature1, temperature2, error_message1, error_message2, ser1, ser2
    while True:
        # --- 1台目のMicro:bit ---
        if ser1:
            try:
                if ser1.in_waiting > 0:
                    data1 = ser1.readline().decode('utf-8').strip()
                    if data1.isdigit():
                        temperature1 = data1
                        error_message1 = None
                    else:
                        temperature1 = None
                        error_message1 = "Invalid data from Micro:bit 1"
                else:
                    # データが取得できない場合は値をクリア
                    temperature1 = None
                    error_message1 = "Micro:bit 1 not connected or no data"
            except Exception as e:
                temperature1 = None
                error_message1 = f"Error reading from Micro:bit 1: {e}"
        else:
            temperature1 = None
            error_message1 = "Micro:bit 1 serial not open"

        # --- 2台目のMicro:bit ---
        if ser2:
            try:
                if ser2.in_waiting > 0:
                    data2 = ser2.readline().decode('utf-8').strip()
                    if data2.isdigit():
                        temperature2 = data2
                        error_message2 = None
                    else:
                        temperature2 = None
                        error_message2 = "Invalid data from Micro:bit 2"
                else:
                    temperature2 = None
                    error_message2 = "Micro:bit 2 not connected or no data"
            except Exception as e:
                temperature2 = None
                error_message2 = f"Error reading from Micro:bit 2: {e}"
        else:
            temperature2 = None
            error_message2 = "Micro:bit 2 serial not open"

        time.sleep(1)

@app.route('/temperature')
def temperature():
    return jsonify({
        'temperature1': temperature1,
        'temperature2': temperature2,
        'error_message1': error_message1,
        'error_message2': error_message2
    })

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # バックグラウンドスレッドで温度データの読み取りを開始
    thread = threading.Thread(target=read_temperature)
    thread.daemon = True  # プログラム終了時にスレッドも終了
    thread.start()
    app.run(debug=True, host='0.0.0.0', port=5002)
