const fs = require('fs');
const jwt = require('jsonwebtoken');
const axios = require('axios');

// API設定
const CONFIG = {
    CLIENT_ID: '***REMOVED***',
    CLIENT_SECRET: '***REMOVED***',
    SERVICE_ACCOUNT: '***REMOVED***',
    PRIVATE_KEY_PATH: './private_20250529134836.key',
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
async function getScheduleByDateRange(startDate, endDate) {
    try {
        const accessToken = await getAccessToken();
        
        const url = `${CONFIG.API_BASE_URL}/users/${CONFIG.USER_ID}/calendar/events`;
        
        const response = await axios.get(url, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json'
            },
            params: {
                fromDateTime: startDate,
                untilDateTime: endDate
            }
        });
        
        console.log(JSON.stringify(response.data));
        
    } catch (error) {
        console.error('ERROR:', error.message);
    }
}

// コマンドライン引数から日付を取得
if (process.argv.length >= 4) {
    const startDate = process.argv[2];
    const endDate = process.argv[3];
    getScheduleByDateRange(startDate, endDate);
} else {
    console.error('Usage: node get_schedule_by_date.js <startDate> <endDate>');
    console.error('Example: node get_schedule_by_date.js 2025-05-30T00:00:00Z 2025-05-31T23:59:59Z');
}