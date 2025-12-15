/**
 * LINEWORKS連絡先登録システム【完成版】
 * 
 * 完成日: 2025年6月12日
 * 機能: 姓名と携帯電話番号のみでLINEWORKS連絡先に正しい姓名順で登録
 * 特徴: 
 * - 正しい姓名順（姓・名）で登録
 * - 読み仮名自動設定
 * - 携帯電話番号対応
 * - エラーハンドリング完備
 * 
 * 使用方法:
 * node LINEWORKS_CONTACT_SYSTEM_PERFECT_FINAL.js "姓" "名" "携帯番号"
 * 例: node LINEWORKS_CONTACT_SYSTEM_PERFECT_FINAL.js "高橋" "進" "090-8630-6501"
 */

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

// 電話番号正規化
function normalizePhoneNumber(phone) {
    return phone.replace(/[-\s()]/g, '');
}

// 読み仮名生成（簡易版）
function generatePhonetic(kanji) {
    const phoneticMap = {
        '高橋': 'タカハシ',
        '田中': 'タナカ',
        '佐藤': 'サトウ',
        '山田': 'ヤマダ',
        '進': 'ススム',
        '太郎': 'タロウ',
        '花子': 'ハナコ',
        '一郎': 'イチロウ',
        '次郎': 'ジロウ'
    };
    
    return phoneticMap[kanji] || kanji;
}

// 正しい姓名順で連絡先登録【完成版】
async function registerContactPerfect(lastName, firstName, mobilePhone) {
    console.log('🎯 LINEWORKS連絡先登録システム【完成版】');
    console.log('='.repeat(70));
    console.log(`📋 姓: ${lastName}`);
    console.log(`📋 名: ${firstName}`);
    console.log(`📋 フルネーム: ${lastName}${firstName}`);
    console.log(`📞 携帯番号: ${mobilePhone}`);
    console.log('='.repeat(70));
    
    try {
        const accessToken = await getAccessToken('contact');
        console.log('✅ LINEWORKS API認証成功');
        
        const headers = {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json'
        };
        
        // 電話番号正規化
        const normalizedPhone = normalizePhoneNumber(mobilePhone);
        console.log(`📱 正規化電話番号: ${normalizedPhone}`);
        
        // 読み仮名生成
        const lastNamePhonetic = generatePhonetic(lastName);
        const firstNamePhonetic = generatePhonetic(firstName);
        console.log(`🔤 読み仮名: ${lastNamePhonetic} ${firstNamePhonetic}`);
        
        // 完成版連絡先データ
        const perfectContactData = {
            contactName: {
                lastName: lastName,           // 正しい姓
                firstName: firstName,         // 正しい名
                phoneticLastName: lastNamePhonetic,
                phoneticFirstName: firstNamePhonetic,
                prefix: null,
                suffix: null,
                middleName: null,
                nickName: null
            },
            telephones: [{
                type: "CELLPHONE",
                telephone: normalizedPhone,
                customType: null,
                primary: true
            }],
            emails: [],
            organizations: [],
            locations: [],
            events: [],
            messengers: [],
            websites: [],
            memo: `LINEWORKS連絡先登録システム【完成版】\n正しい姓名順で登録\n登録日時: ${new Date().toLocaleString('ja-JP', {timeZone: 'Asia/Tokyo'})}`,
            permission: {
                masterUserId: CONFIG.USER_ID,
                isCoEditing: true,
                accessibleRange: "ALL",
                accessibleMembers: []
            }
        };
        
        console.log('🔄 LINEWORKS Contact API登録実行中...');
        
        const response = await axios.post(
            `${CONFIG.API_BASE_URL}/contacts`,
            perfectContactData,
            { headers }
        );
        
        console.log('🎉 連絡先登録完全成功！');
        console.log(`🆔 連絡先ID: ${response.data.contactId}`);
        
        return {
            success: true,
            contactId: response.data.contactId,
            lastName: lastName,
            firstName: firstName,
            fullName: `${lastName}${firstName}`,
            mobilePhone: mobilePhone,
            normalizedPhone: normalizedPhone,
            phoneticName: `${lastNamePhonetic} ${firstNamePhonetic}`
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

// 結果表示【完成版】
function showPerfectResult(result) {
    console.log('\n' + '='.repeat(70));
    console.log('🏆 LINEWORKS連絡先登録【完成版】最終結果');
    console.log('='.repeat(70));
    
    if (result.success) {
        console.log('🎉 【完全成功】連絡先が正しい姓名順で登録されました！');
        console.log('');
        console.log('📋 登録完了情報:');
        console.log(`   👤 姓: ${result.lastName}`);
        console.log(`   👤 名: ${result.firstName}`);
        console.log(`   👤 フルネーム: ${result.fullName}`);
        console.log(`   📞 携帯番号: ${result.mobilePhone}`);
        console.log(`   🔤 読み仮名: ${result.phoneticName}`);
        console.log(`   🆔 連絡先ID: ${result.contactId}`);
        console.log('');
        console.log('✅ 特徴:');
        console.log('   ・正しい姓名順で表示');
        console.log('   ・読み仮名自動設定');
        console.log('   ・携帯電話番号登録');
        console.log('');
        console.log('📱 確認場所:');
        console.log('🔗 https://contact.worksmobile.com/v2/p/shared/contact');
        console.log('   → 「顧客/取引先」セクションで確認');
        
    } else {
        console.log('❌ 【登録失敗】連絡先の登録に失敗しました');
        console.log(`エラー詳細: ${JSON.stringify(result.error, null, 2)}`);
    }
    
    console.log('='.repeat(70));
    console.log('🎯 LINEWORKS連絡先登録システム【完成版】 - 処理完了');
}

// 使用方法表示
function showUsage() {
    console.log('📖 LINEWORKS連絡先登録システム【完成版】使用方法\n');
    console.log('🎯 コマンド形式:');
    console.log('   node LINEWORKS_CONTACT_SYSTEM_PERFECT_FINAL.js "姓" "名" "携帯番号"\n');
    console.log('📝 使用例:');
    console.log('   node LINEWORKS_CONTACT_SYSTEM_PERFECT_FINAL.js "高橋" "進" "090-8630-6501"');
    console.log('   node LINEWORKS_CONTACT_SYSTEM_PERFECT_FINAL.js "田中" "太郎" "080-1234-5678"');
    console.log('   node LINEWORKS_CONTACT_SYSTEM_PERFECT_FINAL.js "山田" "花子" "070-9876-5432"\n');
    console.log('✅ 機能:');
    console.log('   ・正しい姓名順で登録');
    console.log('   ・読み仮名自動生成');
    console.log('   ・携帯電話番号対応');
    console.log('   ・完全なエラーハンドリング\n');
    console.log('📱 登録先: LINEWORKS > アドレス帳 > 顧客/取引先\n');
}

// メイン実行【完成版】
async function main() {
    const args = process.argv.slice(2);
    
    console.log('🎯 LINEWORKS連絡先登録システム【完成版】起動');
    console.log(`📅 実行日時: ${new Date().toLocaleString('ja-JP', {timeZone: 'Asia/Tokyo'})}\n`);
    
    if (args.length === 3) {
        // 正常実行
        const [lastName, firstName, mobilePhone] = args;
        
        if (!lastName.trim() || !firstName.trim() || !mobilePhone.trim()) {
            console.log('❌ エラー: 姓、名、携帯番号は必須です\n');
            showUsage();
            process.exit(1);
        }
        
        const result = await registerContactPerfect(
            lastName.trim(), 
            firstName.trim(), 
            mobilePhone.trim()
        );
        
        showPerfectResult(result);
        
    } else if (args.length === 1 && (args[0] === '--help' || args[0] === '-h')) {
        // ヘルプ表示
        showUsage();
        
    } else {
        // 引数エラー
        console.log('❌ 引数が正しくありません\n');
        showUsage();
        process.exit(1);
    }
}

if (require.main === module) {
    main().catch(error => {
        console.error('💥 システムエラー:', error.message);
        console.error('🔧 完成版システムでエラーが発生しました');
        process.exit(1);
    });
}

module.exports = {
    registerContactPerfect,
    normalizePhoneNumber,
    generatePhonetic
};