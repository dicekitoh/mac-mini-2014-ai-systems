#!/usr/bin/env node
// LINEWORKS カレンダーの6月勤務予定を更新（削除して再作成）

const fs = require('fs');
const crypto = require('crypto');
const https = require('https');

// LINEWORKS API設定
const SERVICE_ACCOUNT = '***REMOVED***';
const CLIENT_ID = '***REMOVED***';
const CLIENT_SECRET = '***REMOVED***';
const PRIVATE_KEY_PATH = './private_20250529134836.key';
const USER_ID = '38067785-e626-4e0c-18d6-05d56a82ed44';

// JWT生成
function generateJWT() {
    const privateKey = fs.readFileSync(PRIVATE_KEY_PATH, 'utf8');
    
    const header = {
        alg: 'RS256',
        typ: 'JWT'
    };
    
    const payload = {
        iss: CLIENT_ID,
        sub: SERVICE_ACCOUNT,
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + 3600
    };
    
    const encodedHeader = Buffer.from(JSON.stringify(header)).toString('base64url');
    const encodedPayload = Buffer.from(JSON.stringify(payload)).toString('base64url');
    
    const sign = crypto.createSign('RSA-SHA256');
    sign.update(encodedHeader + '.' + encodedPayload);
    const signature = sign.sign(privateKey, 'base64url');
    
    return encodedHeader + '.' + encodedPayload + '.' + signature;
}

// アクセストークン取得
function getAccessToken() {
    return new Promise((resolve, reject) => {
        const jwt = generateJWT();
        
        const postData = new URLSearchParams({
            assertion: jwt,
            grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            client_id: CLIENT_ID,
            client_secret: CLIENT_SECRET,
            scope: 'calendar'
        }).toString();
        
        const options = {
            hostname: 'auth.worksmobile.com',
            path: '/oauth2/v2.0/token',
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': Buffer.byteLength(postData)
            }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                if (res.statusCode === 200) {
                    const response = JSON.parse(data);
                    resolve(response.access_token);
                } else {
                    reject(new Error(`Token error: ${res.statusCode} - ${data}`));
                }
            });
        });
        
        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

// カレンダーイベント取得
function getCalendarEvents(accessToken, startDate, endDate) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'www.worksapis.com',
            path: `/v1.0/users/${USER_ID}/calendar/events?fromDateTime=${startDate}&untilDateTime=${endDate}`,
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                if (res.statusCode === 200) {
                    resolve(JSON.parse(data));
                } else {
                    reject(new Error(`Get events error: ${res.statusCode} - ${data}`));
                }
            });
        });
        
        req.on('error', reject);
        req.end();
    });
}

// カレンダーイベント削除
function deleteCalendarEvent(accessToken, eventId) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'www.worksapis.com',
            path: `/v1.0/users/${USER_ID}/calendar/events/${eventId}`,
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                if (res.statusCode === 204 || res.statusCode === 200) {
                    resolve(true);
                } else {
                    reject(new Error(`Delete error: ${res.statusCode} - ${data}`));
                }
            });
        });
        
        req.on('error', reject);
        req.end();
    });
}

// カレンダーイベント作成
function createCalendarEvent(accessToken, eventData) {
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify(eventData);
        
        const options = {
            hostname: 'www.worksapis.com',
            path: `/v1.0/users/${USER_ID}/calendar/events`,
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                if (res.statusCode === 200 || res.statusCode === 201) {
                    resolve(JSON.parse(data));
                } else {
                    reject(new Error(`Event creation error: ${res.statusCode} - ${data}`));
                }
            });
        });
        
        req.on('error', reject);
        req.write(postData);
        req.end();
    });
}

// 勤務タイプに基づいてイベントデータを生成（新しい時間設定）
function createEventData(date, shiftType) {
    const year = 2025;
    const month = 6;
    const day = date;
    
    const shifts = {
        '明け': { allDay: true },
        '夜勤': { start: '16:00', end: '09:00', allDay: false, nextDay: true },
        '日勤': { start: '08:30', end: '17:00', allDay: false },
        '遅番': { start: '10:00', end: '18:30', allDay: false },
        'B勤務': { allDay: true },
        '休み': { allDay: true },
        '有休': { allDay: true }
    };
    
    const shift = shifts[shiftType];
    if (!shift) return null;
    
    const eventData = {
        eventComponents: [{
            summary: `清水理沙子: ${shiftType}`,
            description: `6月勤務予定 - ${shiftType}`,
            attendees: []
        }],
        ical: 'REQUEST'
    };
    
    if (shift.allDay) {
        // 終日イベント
        eventData.eventComponents[0].start = {
            dateTime: `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00`,
            timeZone: 'Asia/Tokyo'
        };
        eventData.eventComponents[0].end = {
            dateTime: `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T00:00:00`,
            timeZone: 'Asia/Tokyo'
        };
        eventData.eventComponents[0].isAllDay = true;
    } else {
        // 時間指定イベント
        const startTime = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T${shift.start}:00`;
        let endTime;
        
        if (shift.nextDay) {
            // 夜勤の場合、終了は翌日
            endTime = `${year}-${String(month).padStart(2, '0')}-${String(day + 1).padStart(2, '0')}T${shift.end}:00`;
        } else {
            endTime = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}T${shift.end}:00`;
        }
        
        eventData.eventComponents[0].start = {
            dateTime: startTime,
            timeZone: 'Asia/Tokyo'
        };
        eventData.eventComponents[0].end = {
            dateTime: endTime,
            timeZone: 'Asia/Tokyo'
        };
    }
    
    return eventData;
}

// メイン処理
async function main() {
    const schedule = [
        '明け', '有休', '有休', '日勤', '休み', '夜勤', '明け', '休み',
        '遅番', '夜勤', '明け', '休み', '日勤', '遅番', '休み', '夜勤',
        '明け', '休み', '休み', '夜勤', '明け', '休み', '日勤', 'B勤務',
        '夜勤', '明け', '休み', 'B勤務', '日勤', '休み'
    ];
    
    try {
        console.log('LINEWORKSカレンダーの6月勤務予定を更新開始...');
        console.log('アクセストークンを取得中...');
        const accessToken = await getAccessToken();
        console.log('アクセストークン取得成功');
        
        // まず6月の既存イベントを取得
        console.log('\n既存の6月イベントを検索中...');
        const events = await getCalendarEvents(accessToken, '2025-06-01T00:00:00', '2025-06-30T23:59:59');
        
        // 清水理沙子の勤務予定のみを削除
        const shimizuEvents = events.events.filter(event => 
            event.summary && event.summary.includes('清水理沙子')
        );
        
        console.log(`${shimizuEvents.length}件の既存イベントが見つかりました`);
        
        // 既存イベントを削除
        if (shimizuEvents.length > 0) {
            console.log('\n既存イベントを削除中...');
            for (const event of shimizuEvents) {
                try {
                    await deleteCalendarEvent(accessToken, event.id);
                    console.log(`削除: ${event.summary}`);
                } catch (error) {
                    console.error(`削除失敗: ${event.summary}`, error.message);
                }
            }
        }
        
        // 新しいイベントを作成
        console.log('\n新しい時間設定でイベントを作成中...');
        console.log('日勤: 8:30-17:00, 遅番: 10:00-18:30, 夜勤: 16:00-翌9:00, その他: 終日');
        
        let successCount = 0;
        
        for (let i = 0; i < schedule.length; i++) {
            const date = i + 1;
            const shiftType = schedule[i];
            const eventData = createEventData(date, shiftType);
            
            if (eventData) {
                try {
                    await createCalendarEvent(accessToken, eventData);
                    console.log(`✅ 6月${date}日: ${shiftType} - 追加成功`);
                    successCount++;
                } catch (error) {
                    console.error(`❌ 6月${date}日: ${shiftType} - 追加失敗:`, error.message);
                }
                
                // レート制限対策のため少し待機
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        }
        
        console.log(`\n完了: ${successCount}/${schedule.length} イベントを追加しました`);
        
    } catch (error) {
        console.error('エラーが発生しました:', error);
    }
}

main();