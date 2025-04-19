/*
  Arduino Pro Micro Stopwatch with Button (A2), External LED (15), and Serial Output

  ボタン（A2ピン）をトリガーにストップウォッチを開始/停止し、
  計測中は接続した外部LED（ピン15）を点灯、停止で消灯させ、
  計測時間をシリアル通信でPCに送信します。
  ボタンのチャタリング対策、ストップウォッチの状態管理、millis()による計測を含みます。
  ボタンはA2ピンにINPUT_PULLUPで配線します。LEDはピン15に抵抗を介して接続します。
*/

// --- 設定 ---
// ボタンを接続したPro MicroのアナログピンA2をデジタルピンとして指定します。
const int buttonPin = A2; // A2ピンを使用

// ストップウォッチ状態表示用のLEDを接続したピン番号を指定します。
const int statusLedPin = 15; // ピン番号15を使用

// ボタンのチャタリング対策のための短い待ち時間 (ミリ秒)
const unsigned long debounceDelay = 50;

// --- 状態管理変数 ---
bool isRunning = false;
unsigned long startTime = 0;
unsigned long stopTime = 0;
int lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;

void setup() {
  Serial.begin(9600); // Python側と合わせる
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(statusLedPin, OUTPUT);
  digitalWrite(statusLedPin, LOW); // 初期状態は消灯 (外部LED想定)
  Serial.println("Stopwatch system ready. Press button to start.");
}

void loop() {
  int reading = digitalRead(buttonPin);

  // --- チャタリング対策と状態変化検出 ---
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != lastButtonState) {
      if (reading == LOW) { // ボタンが押された瞬間
        if (!isRunning) { // 停止中なら開始
          startTime = millis();
          isRunning = true;
          digitalWrite(statusLedPin, HIGH); // LED点灯 (外部LED想定)
          Serial.println("Stopwatch started.");
        } else { // 計測中なら停止
          stopTime = millis();
          isRunning = false;
          digitalWrite(statusLedPin, LOW); // LED消灯 (外部LED想定)
          unsigned long elapsedTime = stopTime - startTime;
          Serial.print("TIME:");
          Serial.println(elapsedTime); // ミリ秒で送信
          Serial.println("Stopwatch stopped. Time sent.");
        }
      }
      lastButtonState = reading; // 安定した状態を記録
    }
  }
  // lastButtonState = reading; // ←この行は上記ifブロック内に移動済み
}