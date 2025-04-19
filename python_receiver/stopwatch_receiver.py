import serial # シリアル通信ライブラリ
import time   # 時間関連ライブラリ
import requests # HTTPリクエストライブラリ
import json   # JSONデータ操作ライブラリ
import sys    # プログラム終了用

# --- 設定項目 ---
# Arduino Pro Microが接続されているシリアルポート名を指定してください。
# (重要！) あなたのPC環境に合わせて正しく設定する必要があります。
# Arduino IDEの「ツール」->「ポート」で確認できます。
# 例:
#   Windows: 'COM3', 'COM4' など
#   macOS: '/dev/cu.usbmodemXXXX' など
#   Linux: '/dev/ttyACM0', '/dev/ttyUSB0' など
SERIAL_PORT = 'SERIAL_PORT' # <<<--- あなたのポート名に修正してください（例：/dev/cu.usbmodem11301）

# Arduinoスケッチで設定したシリアル通信速度 (Serial.begin()の値)
BAUD_RATE = 9600

# Google Apps Scriptで作成し、デプロイしたウェブアプリのURLを指定してください。
# (重要！) GASのデプロイ時に取得したURLを貼り付けてください。
GAS_WEB_APP_URL = 'YOUR_SPREADSHEET_ID_HERE' # <<<--- あなたのGASウェブアプリURLに書き換えてください！

# 接続リトライ設定
RETRY_DELAY_SECONDS = 5 # シリアルポート接続失敗時の再試行間隔（秒）

# --- グローバル変数 ---
ser = None # シリアル接続オブジェクトを保持する変数

# --- シリアルポート接続関数 ---
def connect_serial():
    """シリアルポートへの接続を試みる関数"""
    global ser
    while True:
        try:
            print(f"シリアルポート {SERIAL_PORT} (速度: {BAUD_RATE}) に接続試行中...")
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"シリアルポート {SERIAL_PORT} に接続しました。")
            time.sleep(2) # 接続安定待ち
            print("Arduinoからのデータ受信待機中... ボタンを押して操作してください。")
            return True # 接続成功
        except serial.SerialException as e:
            print(f"エラー: シリアルポート {SERIAL_PORT} を開けません。({e})")
            print(f"{RETRY_DELAY_SECONDS}秒後に再試行します...")
            time.sleep(RETRY_DELAY_SECONDS)
        except Exception as e:
            print(f"予期せぬ接続エラー: {e}")
            print(f"{RETRY_DELAY_SECONDS}秒後に再試行します...")
            time.sleep(RETRY_DELAY_SECONDS)

# --- データ送信関数 ---
def send_to_gas(timestamp, elapsed_ms):
    """計測データをGASウェブアプリに送信する関数"""
    data_to_send = {
        "timestamp": timestamp,
        "elapsedTimeMs": elapsed_ms
    }
    print(f"GASへ送信: {data_to_send}")
    try:
        # GASへHTTP POSTリクエストを送信 (タイムアウトを30秒に設定)
        response = requests.post(GAS_WEB_APP_URL, json=data_to_send, timeout=30)
        response.raise_for_status() # ステータスコードが200番台以外なら例外発生

        # GASからの応答を解析（オプション）
        try:
            response_json = response.json()
            if response_json.get("status") == "success":
                print("GASへのデータ送信成功。")
            else:
                print(f"GASからの応答(成功以外): {response_json}")
        except json.JSONDecodeError:
            print(f"GASからの応答(JSON形式でない): {response.text}")

    except requests.exceptions.Timeout:
        print("エラー: GASへの送信がタイムアウトしました。")
    except requests.exceptions.RequestException as e:
        print(f"エラー: GASへのデータ送信に失敗しました。({e})")
    except Exception as e:
        print(f"エラー: データ送信中に予期せぬエラーが発生しました。({e})")

# --- メイン処理関数 ---
def main_loop():
    """シリアルデータ受信とGASへの送信を行うメインループ"""
    global ser
    while True:
        try:
            # シリアルポートが接続されているか、または接続試行
            if ser is None or not ser.is_open:
                if not connect_serial():
                    # connect_serial内でリトライするので、ここでは待機
                    time.sleep(1)
                    continue

            # データ受信試行
            if ser.in_waiting > 0:
                # 1行読み込み、デコード、前後空白削除
                line = ser.readline().decode('utf-8', errors='ignore').strip()

                # "TIME:"で始まる行かチェック
                if line.startswith("TIME:"):
                    print(f"受信データ: {line}")
                    try:
                        # "TIME:"を除去し、数値に変換
                        elapsed_time_str = line.replace("TIME:", "")
                        elapsed_time_ms = int(elapsed_time_str)

                        # 現在時刻を取得 (YYYY-MM-DD HH:MM:SS形式)
                        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

                        # GASへ送信
                        send_to_gas(current_time, elapsed_time_ms)

                    except ValueError:
                        print(f"エラー: 受信データ '{line}' から数値を抽出できませんでした。")
                    except Exception as e:
                        print(f"エラー: データ処理中に予期せぬエラーが発生しました。({e})")

            # CPU負荷軽減のための短い待機
            time.sleep(0.01)

        except serial.SerialException as e:
            print(f"エラー: シリアル通信中に問題が発生しました。({e})")
            if ser and ser.is_open:
                ser.close()
                print("シリアルポートを閉じました。再接続を試みます...")
            ser = None # 接続オブジェクトをリセット
            time.sleep(RETRY_DELAY_SECONDS) # 再接続前に待機
        except KeyboardInterrupt:
            print("\nプログラムを終了します。(Ctrl+C)")
            break # ループを抜ける
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
            # 予期せぬエラーでも継続試行（状況に応じて変更）
            time.sleep(1)

# --- プログラム実行開始 ---
if __name__ == "__main__":
    try:
        main_loop()
    finally:
        # プログラム終了時に必ずポートを閉じる
        if ser and ser.is_open:
            ser.close()
            print("シリアルポートを閉じました。")
        print("プログラム終了。")
        sys.exit(0) # プログラムを正常終了