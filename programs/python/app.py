import serial
import json
import csv
from flask import Flask, jsonify, render_template
from datetime import datetime
import threading
import time

app = Flask(__name__, template_folder='../html')

# 2つのMicro:bitのポートを指定
PORTS = ["/dev/tty.usbmodem114202", "/dev/tty.usbmodem114302"]
BAUDRATE = 115200

# ポート番号をマッピングして表示名に変換
PORT_NAME_MAP = {
    "/dev/tty.usbmodem114202": "microbit1",
    "/dev/tty.usbmodem114302": "microbit2"
}

# CSVファイルにデータを保存する関数
def save_to_csv(port, temperature):
    filename = "../data/microbit1.csv" if port == PORTS[0] else "../data/microbit2.csv"
    timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    # CSVにデータを書き込む
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, temperature])

def read_temperature(port):
    try:
        with serial.Serial(port, BAUDRATE, timeout=2) as ser:
            raw_data = ser.readline().decode().strip()
            
            # **値の判定**
            if not raw_data:
                return {"error": "エラーコード001: データの取得に失敗しました。ケーブルが抜けていないか確認してください。"}
            if not raw_data.replace('.', '').isdigit():
                return {"error": "エラーコード002: 取得したデータの値が不正です。"}

            temp = float(raw_data)

            # **異常温度の判定**
            if temp > 45:
                return {"error": "エラーコード003: 温度が異常に高いです。", "temperature": temp}
            if temp < 0:
                return {"error": "エラーコード004: 温度が異常に低いです。", "temperature": temp}

            # CSVに保存
            save_to_csv(port, temp)

            # ポート名を返す
            return {"port_name": PORT_NAME_MAP[port], "temperature": temp}

    except Exception as e:
        return {"error": f"{port} の温度の取得に失敗しました。エラー内容: {str(e)}"}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_temperature")
def get_temperature():
    results = {PORT_NAME_MAP[port]: read_temperature(port) for port in PORTS}
    return jsonify(results)

# 温度データを10秒ごとに保存する関数
def save_temperature_periodically():
    while True:
        for port in PORTS:
            read_temperature(port)  # 温度取得と保存
        time.sleep(10)  # 10秒待つ

if __name__ == "__main__":
    # 温度保存の処理を別スレッドで実行
    temperature_thread = threading.Thread(target=save_temperature_periodically)
    temperature_thread.daemon = True  # サーバーが終了するとスレッドも終了
    temperature_thread.start()
    
    # Flaskサーバーを起動
    app.run(host="0.0.0.0", port=8000, debug=True)
