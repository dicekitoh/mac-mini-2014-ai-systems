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

// 正しい姓名順で連絡先登録
async function registerContactCorrectName() {
    console.log('📝 LINEWORKS 正しい姓名順登録システム');
    console.log('='.repeat(60));
    console.log('📋 登録対象: 高橋進（正しい姓名順）');
    console.log('📞 携帯番号: 090-8630-6501');
    console.log('='.repeat(60));
    
    try {
        const accessToken = await getAccessToken('contact');
        console.log('✅ 認証成功');
        
        const headers = {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        };
        
        // 正しい姓名順の連絡先データ
        const correctContactData = {
            contactName: {
                lastName: "高橋",      // 正しい姓
                firstName: "進",       // 正しい名
                phoneticLastName: "タカハシ",
                phoneticFirstName: "ススム",
                prefix: null,
                suffix: null,
                middleName: null,
                nickName: null
            },
            telephones: [{
                type: "CELLPHONE",
                telephone: "09086306501",
                customType: null,
                primary: true
            }],
            emails: [],
            organizations: [],
            locations: [],
            events: [],
            messengers: [],
            websites: [],
            memo: `正しい姓名順で登録\n登録日時: ${new Date().toLocaleString('ja-JP')}`,
            permission: {
                masterUserId: CONFIG.USER_ID,
                isCoEditing: true,
                accessibleRange: "ALL",
                accessibleMembers: []
            }
        };
        
        console.log('🔄 正しい姓名順でLINEWORKS Contact API に登録中...');
        console.log('👤 姓: 高橋, 名: 進');
        
        const response = await axios.post(
            `${CONFIG.API_BASE_URL}/contacts`,
            correctContactData,
            { headers }
        );
        
        console.log('✅ 正しい姓名順での登録成功！');
        console.log(`🆔 連絡先ID: ${response.data.contactId}`);
        
        return {
            success: true,
            contactId: response.data.contactId,
            lastName: "高橋",
            firstName: "進",
            phone: "090-8630-6501"
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
    console.log('📋 正しい姓名順登録 最終結果');
    console.log('='.repeat(60));
    
    if (result.success) {
        console.log('🎉 【登録成功】正しい姓名順で登録されました！');
        console.log(`👤 名前: ${result.lastName}${result.firstName}`);
        console.log(`📞 携帯: ${result.phone}`);
        console.log(`🆔 連絡先ID: ${result.contactId}`);
        console.log('');
        console.log('📱 確認は以下で可能です:');
        console.log('🔗 https://contact.worksmobile.com/v2/p/shared/contact');
        console.log('');
        console.log('💡 姓名が正しい順序で表示されます');
        
    } else {
        console.log('❌ 【登録失敗】正しい姓名順での登録に失敗しました');
        console.log(`エラー: ${JSON.stringify(result.error, null, 2)}`);
    }
    
    console.log('='.repeat(60));
}

// メイン実行
async function main() {
    try {
        const result = await registerContactCorrectName();
        showResult(result);
        
    } catch (error) {
        console.error('❌ システムエラー:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}