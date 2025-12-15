const fs = require('fs');
const jwt = require('jsonwebtoken');
const axios = require('axios');

// LINEWORKS API設定
const CONFIG = {
    CLIENT_ID: '***REMOVED***',
    CLIENT_SECRET: '***REMOVED***', 
    SERVICE_ACCOUNT: '***REMOVED***',
    PRIVATE_KEY_PATH: '/home/rootmax/macmini2014_mount/reservation/private_20250529134836.key',
    AUTH_URL: 'https://auth.worksmobile.com/oauth2/v2.0/token',
    API_BASE_URL: 'https://www.worksapis.com/v1.0',
    USER_ID: '38067785-e626-4e0c-18d6-05d56a82ed44'
};

// JWT作成
function createJWT() {
    const privateKey = fs.readFileSync(CONFIG.PRIVATE_KEY_PATH, 'utf8');
    const now = Math.floor(Date.now() / 1000);
    
    const payload = {
        iss: CONFIG.CLIENT_ID,
        sub: CONFIG.SERVICE_ACCOUNT,
        iat: now,
        exp: now + 3600,
        aud: CONFIG.AUTH_URL
    };
    
    return jwt.sign(payload, privateKey, { algorithm: 'RS256' });
}

// アクセストークン取得
async function getAccessToken(scope) {
    const jwtToken = createJWT();
    
    const data = {
        assertion: jwtToken,
        grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        client_id: CONFIG.CLIENT_ID,
        client_secret: CONFIG.CLIENT_SECRET,
        scope: scope
    };
    
    try {
        const response = await axios.post(CONFIG.AUTH_URL, data, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            transformRequest: [(data) => {
                return Object.keys(data).map(key => `${key}=${encodeURIComponent(data[key])}`).join('&');
            }]
        });
        
        return response.data.access_token;
    } catch (error) {
        throw new Error(`認証失敗 (${scope}): ${error.response?.data?.error || error.message}`);
    }
}

// カレンダーイベントとして連絡先情報を登録
async function registerContactAsEvent() {
    console.log('📅 LINEWORKS カレンダー経由 連絡先登録システム');
    console.log('='.repeat(60));
    console.log('📋 登録対象: 高橋進');
    console.log('📞 携帯番号: 090-8630-6501');
    console.log('='.repeat(60));
    
    try {
        const accessToken = await getAccessToken('calendar');
        console.log('✅ カレンダーAPI認証成功');
        
        const headers = {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        };
        
        // 現在時刻から面会予定を作成
        const now = new Date();
        const startTime = new Date(now.getTime() + 5 * 60 * 1000); // 5分後
        const endTime = new Date(startTime.getTime() + 30 * 60 * 1000); // 30分間
        
        // カレンダーイベントデータ
        const eventData = {
            eventComponents: [{
                type: "VEVENT",
                summary: "面会予約：高橋進",
                description: `連絡先情報\n氏名：高橋進\n携帯：090-8630-6501\n\n※この予定は連絡先情報の保存を目的としています`,
                start: {
                    dateTime: startTime.toISOString(),
                    timeZone: "Asia/Tokyo"
                },
                end: {
                    dateTime: endTime.toISOString(),
                    timeZone: "Asia/Tokyo"
                },
                location: "連絡先登録用",
                attendees: [{
                    email: "dice1019@works-608300",
                    displayName: "高橋進"
                }]
            }]
        };
        
        console.log('📅 カレンダーイベントとして連絡先情報を登録中...');
        
        const response = await axios.post(
            `${CONFIG.API_BASE_URL}/users/${CONFIG.USER_ID}/calendar/events`,
            eventData,
            { headers }
        );
        
        console.log('✅ 連絡先情報の登録成功！');
        console.log(`📅 イベントID: ${response.data.eventId}`);
        console.log(`⏰ 面会予定時間: ${startTime.toLocaleString('ja-JP')}`);
        
        return {
            success: true,
            eventId: response.data.eventId,
            startTime: startTime
        };
        
    } catch (error) {
        console.log(`❌ 登録失敗: ${error.response?.status}: ${error.response?.data?.code}`);
        if (error.response?.data?.description) {
            console.log(`   詳細: ${error.response.data.description}`);
        }
        
        return {
            success: false,
            error: error.response?.data || error.message
        };
    }
}

// 結果表示
function showResult(result) {
    console.log('\n' + '='.repeat(60));
    console.log('📋 LINEWORKS 連絡先登録 最終結果');
    console.log('='.repeat(60));
    
    if (result.success) {
        console.log('🎉 【完全成功】高橋進さんの連絡先情報が登録されました！');
        console.log(`📅 カレンダーイベントID: ${result.eventId}`);
        console.log(`⏰ 面会予定時間: ${result.startTime.toLocaleString('ja-JP')}`);
        console.log('');
        console.log('📱 以下で確認できます:');
        console.log('🔗 カレンダー: https://calendar.worksmobile.com/');
        console.log('🔗 連絡先: https://contact.worksmobile.com/v2/p/shared/contact');
        console.log('');
        console.log('💡 連絡先情報は面会予定の詳細に記録されています');
        
    } else {
        console.log('❌ 【登録失敗】連絡先情報の登録に失敗しました');
        console.log(`エラー: ${JSON.stringify(result.error, null, 2)}`);
    }
    
    console.log('='.repeat(60));
}

// メイン実行
async function main() {
    try {
        const result = await registerContactAsEvent();
        showResult(result);
        
    } catch (error) {
        console.error('❌ システムエラー:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}