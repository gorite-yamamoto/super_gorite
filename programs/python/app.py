import serial
import time
from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='/Users/yamamototakuma/Desktop/python/発表/programs/html')

# シリアルポートの設定
ser = serial.Serial('/dev/tty.usbmodem14302', baudrate=115200, timeout=1)  # Micro:bitのポートを指定

# 温度データを格納するための変数
current_temperature = None

# シリアルポートから温度データを読み取る関数
def read_temperature():
    global current_temperature
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()  # シリアルデータを読み取る
        # 数値データのみを更新
        if data.isdigit():
            current_temperature = data
        else:
            current_temperature = None  # 無効なデータの場合は温度をリセット

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/temperature')
def temperature():
    read_temperature()  # 温度を読み取る
    return jsonify({'temperature': current_temperature})  # JSONで温度データを返す

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
