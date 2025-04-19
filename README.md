# Pro Micro ストップウォッチロガー

Arduino Pro Micro、Python、Google Apps Script を使って、物理ボタンで操作するストップウォッチの計測時間をGoogleスプレッドシートに記録するシステムです。

## システム構成

- **入力/計測**: Arduino Pro Micro + タクトスイッチ(A2) + LED(15)
- **データ中継**: PC上のPythonスクリプト (シリアル受信 -> GASへPOST)
- **データ記録**: Google Apps Script Web App -> Googleスプレッドシート

## 必要なもの

### ハードウェア
- Arduino Pro Micro (または互換ボード)
- USBケーブル (Micro B)
- タクトスイッチ 1個
- LED 1個
- 抵抗 1個 (例: 220Ω or 330Ω for LED)
- ブレッドボードとジャンパーワイヤ

### ソフトウェア・アカウント
- Arduino IDE
- Python 3.x
- `pyserial` と `requests` Pythonライブラリ
- Googleアカウント

## ディレクトリ構成
stopwatch_logger/
├── arduino_promicro/
│   └── stopwatch_promicro.ino
├── python_receiver/
│   ├── stopwatch_receiver.py
│   └── requirements.txt
├── gas_webapp/
│   └── Code.gs
└── README.md


## セットアップ手順

1.  **ハードウェア配線**:
    - タクトスイッチの一方を Pro Micro の A2 ピン、もう一方を GND ピンに接続。
    - LEDのアノード（長い足）を Pro Micro の 15 ピンに接続。
    - LEDのカソード（短い足）を抵抗経由で GND ピンに接続。

2.  **Arduino**:
    - `arduino_promicro/stopwatch_promicro.ino` を Arduino IDE で開く。
    - ボードを「Arduino Leonardo」、ポートを Pro Micro が接続されているものに設定。
    - スケッチを Pro Micro に書き込む。

3.  **Google スプレッドシート**:
    - 新しい Google スプレッドシートを作成する。
    - スプレッドシートのURLから **スプレッドシートID** をコピーする（例: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit` の `SPREADSHEET_ID_HERE` 部分）。
    - 記録したいシート名を決める（例: `計測ログ`）。

4.  **Google Apps Script (GAS)**:
    - スプレッドシートの「ツール」>「スクリプトエディタ」を開く。
    - `gas_webapp/Code.gs` の内容をスクリプトエディタに貼り付ける。
    - コード内の `YOUR_SPREADSHEET_ID_HERE` を手順3でコピーした **スプレッドシートID** に書き換える。
    - コード内の `YOUR_SHEET_NAME_HERE` を手順3で決めた **シート名** に書き換える（デフォルトは `計測ログ`）。
    - スクリプトを保存する（プロジェクト名を付ける）。
    - 右上の「デプロイ」>「新しいデプロイ」をクリック。
    - 種類の選択で「ウェブアプリ」を選択。
    - 説明を入力（任意）。
    - 「実行ユーザー」を「自分」に設定。
    - **「アクセスできるユーザー」を「全員」に設定**（重要）。
    - 「デプロイ」をクリック。承認を求められたら許可する。
    - 表示される **ウェブアプリのURL** をコピーする。

5.  **Python**:
    - PCにPython3がインストールされていることを確認する。
    - ターミナル（コマンドプロンプト）を開き、`python_receiver` ディレクトリに移動する。
    - 必要なライブラリをインストールする: `pip install -r requirements.txt`
    - `python_receiver/stopwatch_receiver.py` をテキストエディタで開く。
    - `SERIAL_PORT = '/dev/cu.usbmodem11301'` の部分が自分の環境のポート名と合っているか確認・修正する。
    - `GAS_WEB_APP_URL = 'YOUR_GAS_WEB_APP_URL_HERE'` の部分を、手順4でコピーした **ウェブアプリのURL** に書き換える。
    - ファイルを保存する。

6.  **実行**:
    - Pro Micro を PC に接続する。
    - **Arduino IDE のシリアルモニタは閉じておく**。
    - ターミナルで `python_receiver` ディレクトリにいることを確認し、以下のコマンドでPythonスクリプトを実行する: `python stopwatch_receiver.py`
    - ターミナルに「Arduinoからのデータ受信待機中...」と表示されたら、Pro Micro のボタンを押してストップウォッチを開始・停止させる。
    - 停止時に、ターミナルにログが表示され、Google スプレッドシートにデータが追記されることを確認する。
    - スクリプトを終了するには、ターミナルで `Ctrl + C` を押す。

## トラブルシューティング

- **Pythonがポートを開けない**: `SERIAL_PORT` の設定が正しいか、Arduino IDEのシリアルモニタが閉まっているか確認。
- **GASにデータが送信されない**: `GAS_WEB_APP_URL` が正しいか、GASが正しくデプロイされているか（アクセス権が「全員」になっているか）確認。Python側のエラーメッセージも確認。
- **スプレッドシートに記録されない**: GASコードの `SPREADSHEET_ID` と `SHEET_NAME` が正しいか確認。GASの実行ログ（スクリプトエディタの左メニュー「実行数」）も確認。

3. Google スプレッドシート構成

GASコードに合わせて、以下のような構成のスプレッドシートを用意することをお勧めします。

シート名: 計測ログ （またはGASコードで指定した名前）
ヘッダー行（1行目）:
A1: 記録日時
B1: 計測時間(ミリ秒)
C1: 計測時間(秒)
データ行（2行目以降）:
A列: PythonスクリプトがGASに送信したときのPC時刻 (例: 2025-04-19 15:55:10)
B列: Pro Microが計測した時間 (例: 3500)
C列: GASがB列の値を1000で割って計算した値 (例: 3.500)
GASコードは、シートが存在しない場合や空の場合に自動でこのヘッダー行を追加するようにしてあります。