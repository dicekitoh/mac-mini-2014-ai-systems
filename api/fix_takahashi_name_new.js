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

// 修正対象の連絡先情報（最新）
const CONTACT_INFO = {
    contactId: 'de5b6558-6ae8-411b-5ee5-05433503d07d',
    correctLastName: '高橋',    // 正しい姓
    correctFirstName: '進',     // 正しい名
    phone: '09086306501'
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

// 連絡先情報取得
async function getContactInfo(contactId, accessToken) {
    const headers = {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    };
    
    try {
        const response = await axios.get(
            `${CONFIG.API_BASE_URL}/contacts/${contactId}`,
            { headers }
        );
        
        return response.data;
    } catch (error) {
        throw new Error(`連絡先情報取得失敗: ${error.response?.status}: ${error.response?.data?.code || error.message}`);
    }
}

// 連絡先の姓名修正
async function fixContactName(contactId, correctLastName, correctFirstName, accessToken) {
    const headers = {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    };
    
    // 現在の連絡先情報を取得
    const currentContact = await getContactInfo(contactId, accessToken);
    
    console.log('📋 現在の連絡先情報:');
    console.log(`   姓: ${currentContact.contactName?.lastName || '未設定'}`);
    console.log(`   名: ${currentContact.contactName?.firstName || '未設定'}`);
    
    // 修正後の連絡先データ
    const updatedContactData = {
        ...currentContact,
        contactName: {
            ...currentContact.contactName,
            lastName: correctLastName,
            firstName: correctFirstName,
            phoneticLastName: "",
            phoneticFirstName: ""
        }
    };
    
    try {
        const response = await axios.patch(
            `${CONFIG.API_BASE_URL}/contacts/${contactId}`,
            updatedContactData,
            { headers }
        );
        
        return {
            success: true,
            contactId: contactId,
            lastName: correctLastName,
            firstName: correctFirstName
        };
        
    } catch (error) {
        throw new Error(`姓名修正失敗: ${error.response?.status}: ${error.response?.data?.code || error.message}`);
    }
}

// 姓名修正実行
async function fixContactNameMain() {
    console.log('🔧 連絡先姓名修正システム');
    console.log('='.repeat(50));
    console.log(`🆔 連絡先ID: ${CONTACT_INFO.contactId}`);
    console.log(`✅ 正しい姓: ${CONTACT_INFO.correctLastName}`);
    console.log(`✅ 正しい名: ${CONTACT_INFO.correctFirstName}`);
    console.log('='.repeat(50));
    
    try {
        const accessToken = await getAccessToken('contact');
        console.log('✅ 認証成功');
        
        const result = await fixContactName(
            CONTACT_INFO.contactId,
            CONTACT_INFO.correctLastName,
            CONTACT_INFO.correctFirstName,
            accessToken
        );
        
        console.log('✅ 姓名修正成功！');
        console.log(`📝 修正後: ${result.lastName}${result.firstName}`);
        
        return result;
        
    } catch (error) {
        console.log(`❌ 修正失敗: ${error.message}`);
        
        return {
            success: false,
            error: error.message
        };
    }
}

// 結果表示
function showResult(result) {
    console.log('\n' + '='.repeat(50));
    console.log('📋 姓名修正 最終結果');
    console.log('='.repeat(50));
    
    if (result.success) {
        console.log('🎉 【修正成功】姓名が正しく修正されました！');
        console.log(`👤 修正後の名前: ${result.lastName}${result.firstName}`);
        console.log(`🆔 連絡先ID: ${result.contactId}`);
        console.log('');
        console.log('📱 確認は以下で可能です:');
        console.log('🔗 https://contact.worksmobile.com/v2/p/shared/contact');
        
    } else {
        console.log('❌ 【修正失敗】姓名の修正に失敗しました');
        console.log(`エラー: ${JSON.stringify(result.error, null, 2)}`);
    }
    
    console.log('='.repeat(50));
}

// メイン実行
async function main() {
    try {
        const result = await fixContactNameMain();
        showResult(result);
        
    } catch (error) {
        console.error('❌ システムエラー:', error.message);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}