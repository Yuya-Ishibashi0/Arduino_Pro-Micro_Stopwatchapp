// --- 設定 ---
// データを記録したいGoogleスプレッドシートのIDを指定します。
// スプレッドシートのURLの https://docs.google.com/spreadsheets/d/ ここから /edit の間の部分です。
const SPREADSHEET_ID = 'SPREADSHEET_ID_HERE'; // <<<--- ここを必ず書き換えてください！

// データを書き込みたいシートの名前を指定します。
const SHEET_NAME = '計測ログ'; // <<<--- ここを必要なら書き換えてください！ 例: 'Sheet1'

// --- 定数 ---
const HEADER_ROW = ['記録日時', '計測時間(ミリ秒)', '計測時間(秒)']; // スプレッドシートのヘッダー行

/**
 * HTTP POSTリクエストを受信したときに実行されるメイン関数。
 * Pythonから送信されたタイムスタンプと計測時間(ms)をスプレッドシートに記録します。
 * @param {Object} e - POSTリクエストイベントオブジェクト
 * @return {ContentService.TextOutput} - 処理結果を示すJSON応答
 */
function doPost(e) {
  let response = { status: "error", message: "Unknown error" };
  let spreadsheet;
  let sheet;

  try {
    // スプレッドシートとシートを取得、存在しなければ作成
    try {
      spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
      sheet = spreadsheet.getSheetByName(SHEET_NAME);
      if (!sheet) {
        sheet = spreadsheet.insertSheet(SHEET_NAME);
        sheet.appendRow(HEADER_ROW); // 新規シートにヘッダーを追加
        console.log(`シート '${SHEET_NAME}' が存在しなかったため作成し、ヘッダーを追加しました。`);
      } else if (sheet.getLastRow() === 0) {
        sheet.appendRow(HEADER_ROW); // 既存シートが空ならヘッダーを追加
         console.log(`シート '${SHEET_NAME}' が空だったためヘッダーを追加しました。`);
      }
    } catch (err) {
      console.error(`スプレッドシートまたはシートを開けません (${SPREADSHEET_ID}, ${SHEET_NAME}): ${err}`);
      throw new Error(`スプレッドシート(ID: ${SPREADSHEET_ID})またはシート(名前: ${SHEET_NAME})が見つからないか、アクセス権がありません。`);
    }

    // POSTデータの内容を確認し、JSONとしてパース
    if (!e || !e.postData || !e.postData.contents) {
      throw new Error("POSTデータが空です。");
    }
    let requestBody;
    try {
      requestBody = JSON.parse(e.postData.contents);
    } catch (parseError) {
      throw new Error(`POSTデータのJSONパースに失敗しました: ${parseError} (受信内容: ${e.postData.contents})`);
    }

    // 必要なデータがJSONに含まれているか確認
    const timestamp = requestBody.timestamp; // Pythonから送られるキー名 'timestamp'
    const elapsedTimeMs = requestBody.elapsedTimeMs; // Pythonから送られるキー名 'elapsedTimeMs'

    if (timestamp === undefined || elapsedTimeMs === undefined) {
      throw new Error("POSTデータに必要なキー（timestamp, elapsedTimeMs）が含まれていません。");
    }
    if (typeof elapsedTimeMs !== 'number') {
       throw new Error(`elapsedTimeMsの値(${elapsedTimeMs})が数値ではありません。`);
    }

    // ミリ秒から秒に変換 (小数点以下3桁まで)
    const elapsedTimeSec = (elapsedTimeMs / 1000).toFixed(3);

    // スプレッドシートにデータを追記
    sheet.appendRow([timestamp, elapsedTimeMs, elapsedTimeSec]);
    console.log(`データを記録しました: ${timestamp}, ${elapsedTimeMs} ms, ${elapsedTimeSec} s`);

    // 成功応答を設定
    response = { status: "success", message: "Data logged successfully" };

  } catch (error) {
    // エラー処理
    console.error(`エラー発生: ${error.stack || error}`);
    response = { status: "error", message: error.message };
  }

  // 最終的な応答をJSON形式で返す (CORSヘッダー付き)
  return ContentService.createTextOutput(JSON.stringify(response))
    .setMimeType(ContentService.MimeType.JSON)
    .setHeader('Access-Control-Allow-Origin', '*') // 全てのオリジンからのアクセスを許可（必要に応じて制限）
    .setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
    .setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

/**
 * OPTIONSリクエスト（プリフライトリクエスト）に対応するための関数。
 * CORS設定のために必要です。
 * @param {Object} e - OPTIONSリクエストイベントオブジェクト
 * @return {ContentService.TextOutput} - CORS許可ヘッダーを含む応答
 */
function doOptions(e) {
  return ContentService.createTextOutput()
    .setHeader('Access-Control-Allow-Origin', '*')
    .setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS')
    .setHeader('Access-Control-Allow-Headers', 'Content-Type');
}

// doGetは今回使用しないが、ウェブアプリとしては定義しておく方が一般的
function doGet(e) {
  return ContentService.createTextOutput("このURLはPOSTリクエスト専用です。");
}