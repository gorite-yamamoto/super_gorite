from flask import Flask, render_template, jsonify
import serial

app = Flask(__name__, template_folder='../html')

# シリアルポートと通信速度の設定
SERIAL_PORT = '/dev/tty.usbmodem114302'  # 実際のポートに合わせてください
BAUD_RATE = 115200

def serial_read_temperature():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            line = ser.readline().decode('utf-8').strip()
            
            # 数字以外が含まれている場合、エラー002を返す
            try:
                temperature = float(line)
            except ValueError:
                # 温度データが不正な場合（英字や不正な数値）
                return {"error": "002", "temperature": None}

            # ここで温度が0~45℃の範囲に収まっているかチェック
            if temperature < 0:
                # 低温異常 (エラー004)
                return {"error": "004", "temperature": None}
            elif temperature > 45:
                # 高温異常 (エラー003)
                return {"error": "003", "temperature": None}

            # 正常な範囲内であれば、データを返す
            return {"error": None, "temperature": temperature}
    
    except serial.SerialException:
        # シリアルポートが開けなかった場合 (エラー001)
        return {"error": "001", "temperature": None}

@app.route('/')
def index():
    # 温度を取得して結果を返す
    result = serial_read_temperature()

    if result["error"]:
        # エラーが発生した場合
        if result["error"] == "002":
            # エラー002の場合、003または004のチェックを行う
            error_message = "データの取得に失敗しました。ケーブルを一度抜くか、時間を置いてから再度実行、またはmicrobitのコードを確認してください。"
            if result["temperature"] is None:
                return render_template('index.html', error=result["error"], error_message=error_message)
        
        if result["error"] == "001":
            # ケーブルが抜けた場合
            return render_template('index.html', error="001", error_message="ケーブルが抜けているか接続に失敗しました。再接続を試みてください。")
        
        if result["error"] == "003":
            # 高温異常
            return render_template('index.html', error="003", error_message="microbitの温度が異常に高いです。炎天下などで使用していないか確認してください。正常な動作範囲は0~45℃です。")
        
        if result["error"] == "004":
            # 低温異常
            return render_template('index.html', error="004", error_message="microbitの温度が異常に低いです。冷凍庫などで使用していないか確認してください。正常な動作範囲は0~45℃です。")
    
    # 正常な温度が取得できた場合
    return render_template('index.html', error=None, temperature=result["temperature"])

@app.route('/get_temperature')
def get_temperature():
    # 温度データをJSON形式で返す
    result = serial_read_temperature()

    if result["error"]:
        return jsonify({"error": result["error"], "temperature": None})
    
    return jsonify({"error": None, "temperature": result["temperature"]})

if __name__ == '__main__':
    app.run(debug=True)
