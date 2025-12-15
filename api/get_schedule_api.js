const fs = require('fs');
const jwt = require('jsonwebtoken');
const axios = require('axios');

// API設定（正しいUUID使用）
const CONFIG = {
    CLIENT_ID: '***REMOVED***',
    CLIENT_SECRET: '***REMOVED***', 
    SERVICE_ACCOUNT: '***REMOVED***',
    PRIVATE_KEY_PATH: './private_20250529134836.key',
    AUTH_URL: 'https://auth.worksmobile.com/oauth2/v2.0/token',
    API_BASE_URL: 'https://www.worksapis.com/v1.0',
    USER_ID: '38067785-e626-4e0c-18d6-05d56a82ed44'  // 正しいUUID
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
async function getAccessToken() {
    const jwtToken = createJWT();
    
    const data = {
        assertion: jwtToken,
        grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        client_id: CONFIG.CLIENT_ID,
        client_secret: CONFIG.CLIENT_SECRET,
        scope: 'calendar calendar.read'
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
        console.error('認証エラー:', error.response?.data || error.message);
        throw error;
    }
}

// スケジュール取得
async function getSchedule() {
    console.log('🚀 LINEWORKS スケジュール取得');
    console.log('=====================================\n');
    
    try {
        console.log('🔐 認証中...');
        const accessToken = await getAccessToken();
        console.log('✅ 認証成功\n');
        
        // 今日から7日間のスケジュール
        const today = new Date();
        const endDate = new Date(today);
        endDate.setDate(today.getDate() + 7);
        
        // UTCで開始時刻と終了時刻を設定
        const fromDateTime = new Date(today.setHours(0, 0, 0, 0) - today.getTimezoneOffset() * 60000).toISOString();
        const untilDateTime = new Date(endDate.setHours(23, 59, 59, 999) - endDate.getTimezoneOffset() * 60000).toISOString();
        
        console.log(`📅 取得期間: ${today.toLocaleDateString('ja-JP')} ～ ${endDate.toLocaleDateString('ja-JP')}`);
        
        const url = `${CONFIG.API_BASE_URL}/users/${CONFIG.USER_ID}/calendar/events`;
        console.log(`📋 エンドポイント: ${url}\n`);
        
        const response = await axios.get(url, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            params: {
                fromDateTime: fromDateTime,
                untilDateTime: untilDateTime
            }
        });
        
        const events = response.data.events || [];
        console.log(`✅ ${events.length}件のイベントを取得しました\n`);
        
        if (events.length > 0) {
            console.log('📋 スケジュール詳細:');
            console.log('========================\n');
            
            events.forEach((eventGroup, groupIndex) => {
                const eventComponents = eventGroup.eventComponents || [];
                
                eventComponents.forEach((event, index) => {
                    console.log(`【${groupIndex + 1}-${index + 1}】 ${event.summary || '(タイトルなし)'}`);
                    
                    // 開始時刻と終了時刻
                    if (event.start?.dateTime) {
                        const start = new Date(event.start.dateTime);
                        const end = new Date(event.end.dateTime);
                        console.log(`   日時: ${start.toLocaleString('ja-JP')} ～ ${end.toLocaleTimeString('ja-JP')}`);
                    } else if (event.start?.date) {
                        console.log(`   日付: ${event.start.date} (終日)`);
                    }
                    
                    // その他の情報
                    if (event.description) {
                        console.log(`   詳細: ${event.description}`);
                    }
                    if (event.location) {
                        console.log(`   場所: ${event.location}`);
                    }
                    if (event.attendees?.length > 0) {
                        console.log(`   参加者: ${event.attendees.length}名`);
                    }
                    if (event.recurrenceRule) {
                        console.log(`   繰り返し: あり`);
                    }
                    
                    console.log(`   作成日時: ${new Date(event.createdTime.dateTime).toLocaleString('ja-JP')}`);
                    console.log(`   表示URL: ${event.viewUrl}`);
                    console.log();
                });
            });
        } else {
            console.log('指定期間にイベントはありません。');
        }
        
        // データをファイルに保存
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
        const filename = `schedule_data_${timestamp}.json`;
        const saveData = {
            timestamp: new Date().toISOString(),
            period: {
                from: fromDateTime,
                until: untilDateTime
            },
            count: events.length,
            events: events
        };
        
        fs.writeFileSync(filename, JSON.stringify(saveData, null, 2));
        console.log(`\n💾 データを保存しました: ${filename}`);
        
        return events;
        
    } catch (error) {
        console.error('\n❌ エラーが発生しました:');
        if (error.response) {
            console.error('  ステータス:', error.response.status);
            console.error('  詳細:', error.response.data);
        } else {
            console.error('  メッセージ:', error.message);
        }
        throw error;
    }
}

// 実行
if (require.main === module) {
    getSchedule()
        .then(() => {
            console.log('\n✅ スケジュール取得完了');
        })
        .catch(() => {
            console.log('\n❌ スケジュール取得失敗');
            process.exit(1);
        });
}

module.exports = { getSchedule };