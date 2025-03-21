from flask import Flask, render_template, jsonify
import serial
import threading
import time

app = Flask(__name__)

# シリアルポートの設定（適宜変更してください）
SERIAL_PORT = '/dev/tty.usbmodem114302'  # Micro:bitが接続されているポート
BAUD_RATE = 115200

# 温度データを保持する変数
current_temperature = None

# シリアル通信からデータを読み取る関数
def read_temperature():
    global current_temperature
    with serial.Serial(SERIAL_PORT, BAUD_RATE) as ser:
        while True:
            if ser.in_waiting > 0:
                try:
                    temp = ser.readline().decode('utf-8').strip()  # シリアルから読み取った温度をデコード
                    current_temperature = temp  # 現在の温度を更新
                except Exception as e:
                    print(f"Error reading data: {e}")
            time.sleep(1)

# データ更新用のスレッドを開始
thread = threading.Thread(target=read_temperature)
thread.daemon = True  # プログラム終了時にスレッドも終了
thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/temperature')
def temperature():
    return jsonify(temperature=current_temperature)

if __name__ == '__main__':
    app.run(debug=True)
