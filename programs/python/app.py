import serial
import csv
import json
import requests
from flask import Flask, jsonify, render_template
from datetime import datetime
import math

app = Flask(__name__, template_folder='../html')

# 2つのMicro:bitのポートを指定
PORTS = {
    "/dev/tty.usbmodem114202": "microbit1",
    "/dev/tty.usbmodem114302": "microbit2"
}
BAUDRATE = 115200

# CSVファイルのパス
CSV_PATH = "../data"

# OpenWeatherMap APIキーとURL設定
API_KEY = "1a67f45518babc6a7ca1e172dea06a80"  # あなたのAPIキーをここに設定
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?q=Hiroshima,JP&appid=" + API_KEY + "&units=metric&lang=ja"

# 温度の読み取り
def read_temperature(port):
    try:
        # ポートに応じたシリアル通信
        with serial.Serial(port, BAUDRATE, timeout=2) as ser:
            raw_data = ser.readline().decode().strip()

            # データの判定
            if not raw_data:
                return {"error": "エラーコード001: データの取得に失敗しました。ケーブルが抜けていないか確認してください。"}
            if not raw_data.replace('.', '').isdigit():
                return {"error": "エラーコード002: 取得したデータの値が不正です。"}

            temp = float(raw_data)

            # 異常温度の判定
            if temp > 45:
                return {"error": "エラーコード003: 温度が異常に高いです。", "temperature": temp}
            if temp < 0:
                return {"error": "エラーコード004: 温度が異常に低いです。", "temperature": temp}

            return {"temperature": temp}

    except Exception as e:
        return {"error": f"{port} の温度の取得に失敗しました。エラー内容: {str(e)}"}

# CSVから前回の温度を読み取る（安全に処理）
def read_previous_temperature(port):
    filename = f"{CSV_PATH}/{PORTS[port]}.csv"
    try:
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            rows = list(reader)
            if rows:
                last_temp = rows[-1][1].strip()  # 空白を削除
                if last_temp:  # 値が空じゃないかチェック
                    return round(float(last_temp))  # 四捨五入
    except (FileNotFoundError, ValueError, IndexError):
        return "--"  # ファイルなし・変換エラー・データなし時

    return "--"  # デフォルト値

# CSVに温度を書き込む
def write_temperature_to_csv(temperature):
    filename = "../data/weathertemp.csv"
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        timestamp = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        writer.writerow([timestamp, temperature])

# 天気予報を取得
def get_weather():
    try:
        response = requests.get(WEATHER_URL)
        weather_data = response.json()
        if weather_data.get("main"):
            temp = round(weather_data["main"]["temp"])
            weather_description = weather_data["weather"][0]["description"]
            return {"temperature": temp, "description": weather_description}
        else:
            return {"error": "天気予報の取得に失敗しました。"}
    except Exception as e:
        return {"error": f"天気予報の取得に失敗しました。エラー内容: {str(e)}"}

# OpenWeatherMapの気温を基準に熱中症危険度を判定する
def get_heatstroke_risk(temperature):
    if temperature >= 35:
        return "危険"
    elif 31 <= temperature < 35:
        return "厳重警戒"
    elif 28 <= temperature < 31:
        return "警戒"
    elif 24 <= temperature < 28:
        return "注意"
    else:
        return "安全"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_temperature")
def get_temperature():
    results = {}

    # 温度データの取得
    for port in PORTS.keys():
        temp_data = read_temperature(port)
        previous_temp = read_previous_temperature(port)
        if "temperature" in temp_data:
            current_temp = temp_data["temperature"]
            write_temperature_to_csv(current_temp)
            results[PORTS[port]] = {
                "current_temp": current_temp,
                "previous_temp": previous_temp,
                "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            }
        else:
            results[PORTS[port]] = {
                "error": temp_data["error"],
                "previous_temp": previous_temp,
                "time": datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            }

    # 天気情報の取得
    weather_data = get_weather()
    results["weather"] = weather_data
    if weather_data.get("temperature"):
        heatstroke_risk_level = get_heatstroke_risk(weather_data["temperature"]) # 変数名変更
        results["heatstroke_risk_level"] = heatstroke_risk_level # 変数名変更
    else:
        results["heatstroke_risk_level"] = "気温データなし" # 変数名変更

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)