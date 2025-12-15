<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// OPTIONSリクエストの処理
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// POSTリクエストのみ受け付け
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit();
}

// 入力データを取得
$input = json_decode(file_get_contents('php://input'), true);

if (!$input) {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid JSON input']);
    exit();
}

// 必須フィールドの確認
$required_fields = ['userName', 'visitorName', 'date', 'time'];
foreach ($required_fields as $field) {
    if (empty($input[$field])) {
        http_response_code(400);
        echo json_encode(['error' => "Missing required field: $field"]);
        exit();
    }
}

// LINEWORKS API設定
$config = [
    'service_account' => '***REMOVED***',
    'client_id' => '***REMOVED***',
    'client_secret' => '***REMOVED***',
    'user_id' => '38067785-e626-4e0c-18d6-05d56a82ed44',
    'private_key_path' => '/var/www/html/private_20250529134836.key'
];

// JWTトークン生成
function createJWT($config) {
    $header = json_encode(['typ' => 'JWT', 'alg' => 'RS256']);
    $now = time();
    $payload = json_encode([
        'iss' => $config['service_account'],
        'sub' => $config['client_id'],
        'aud' => 'https://auth.worksmobile.com/oauth2/v2.0/token',
        'exp' => $now + 3600,
        'iat' => $now
    ]);

    $base64Header = str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($header));
    $base64Payload = str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($payload));
    
    $signature_input = $base64Header . '.' . $base64Payload;
    
    if (!file_exists($config['private_key_path'])) {
        throw new Exception('Private key file not found');
    }
    
    $private_key = file_get_contents($config['private_key_path']);
    openssl_sign($signature_input, $signature, $private_key, OPENSSL_ALGO_SHA256);
    $base64Signature = str_replace(['+', '/', '='], ['-', '_', ''], base64_encode($signature));
    
    return $signature_input . '.' . $base64Signature;
}

// アクセストークン取得
function getAccessToken($config) {
    try {
        $jwt = createJWT($config);
        
        $postData = [
            'grant_type' => 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion' => $jwt,
            'scope' => 'calendar'
        ];
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => 'https://auth.worksmobile.com/oauth2/v2.0/token',
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => http_build_query($postData),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/x-www-form-urlencoded'
            ]
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200) {
            throw new Exception("Token request failed with HTTP $httpCode: $response");
        }
        
        $tokenData = json_decode($response, true);
        if (!$tokenData || !isset($tokenData['access_token'])) {
            throw new Exception('Invalid token response');
        }
        
        return $tokenData['access_token'];
    } catch (Exception $e) {
        throw new Exception('Token generation failed: ' . $e->getMessage());
    }
}

// カレンダーイベント作成
function createCalendarEvent($config, $accessToken, $eventData) {
    $url = "https://www.worksapis.com/v1.0/users/{$config['user_id']}/calendar/events";
    
    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($eventData),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => [
            'Authorization: Bearer ' . $accessToken,
            'Content-Type: application/json'
        ]
    ]);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 201) {
        return json_decode($response, true);
    } else {
        throw new Exception("Calendar API failed with HTTP $httpCode: $response");
    }
}

// 時間に30分を追加する関数
function addMinutes($time, $minutes) {
    $timestamp = strtotime($time);
    return date('H:i', $timestamp + ($minutes * 60));
}

try {
    // アクセストークン取得
    $accessToken = getAccessToken($config);
    
    // イベントデータ作成
    $startTime = $input['date'] . 'T' . $input['time'] . ':00+09:00';
    $endTime = $input['date'] . 'T' . addMinutes($input['time'], 30) . ':00+09:00';
    
    $eventData = [
        'title' => "面会予約：{$input['userName']} ← {$input['visitorName']}",
        'start' => $startTime,
        'end' => $endTime,
        'description' => "利用者：{$input['userName']}\n面会者：{$input['visitorName']}\n\n※面会予約システムから自動登録"
    ];
    
    // カレンダーイベント作成
    $result = createCalendarEvent($config, $accessToken, $eventData);
    
    // 成功レスポンス
    echo json_encode([
        'success' => true,
        'message' => 'LINEWORKSスケジュールに登録されました',
        'event_id' => $result['id'] ?? null,
        'event_data' => $eventData
    ]);
    
} catch (Exception $e) {
    error_log("LINEWORKS API Error: " . $e->getMessage());
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'スケジュール登録に失敗しました',
        'details' => $e->getMessage()
    ]);
}
?>