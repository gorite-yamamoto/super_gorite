from microbit import *
import ustruct

while True:
    temperature = temperature()  # 温度を取得
    uart.write(ustruct.pack('h', temperature))  # シリアル通信で送信
    sleep(1000)  # 1秒間隔で送信
