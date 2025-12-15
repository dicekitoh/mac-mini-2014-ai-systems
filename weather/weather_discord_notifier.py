#!/usr/bin/env python3
"""
天気条件Discord自動通知システム
- 手稲区の最高気温25度超え
- 清田区の朝8時雨予報
条件に該当する場合、即座にDiscord通知
"""
import requests
from datetime import datetime, timedelta, timezone
import json
import time
import os

class WeatherDiscordNotifier:
    def __init__(self):
        # Discord設定を読み込み
        self.load_discord_config()
        
        # ユーザーDiscord ID
        self.user_discord_id = "1387371662671876118"
        
        # 手稲区の座標
        self.teine_coords = {
            "name": "札幌市手稲区",
            "lat": 43.1236,
            "lon": 141.2469
        }
        
        # 清田区の座標
        self.kiyota_coords = {
            "name": "札幌市清田区", 
            "lat": 43.0064,
            "lon": 141.4064
        }
        
        # 通知済み記録ファイル
        self.notified_file = "/home/fujinosuke/weather_notifications_sent.json"
        
        # 通知履歴読み込み
        self.notified_dates = self.load_notification_history()
    
    def load_discord_config(self):
        """Discord設定を読み込み"""
        try:
            config_file = "/home/fujinosuke/user_discord_config.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.webhook_url = config.get("discord_settings", {}).get("webhook_url", "")
            
            if not self.webhook_url:
                raise ValueError("Discord Webhook URLが設定されていません")
                
            print(f"✅ Discord設定読み込み完了")
            
        except Exception as e:
            print(f"❌ Discord設定読み込みエラー: {e}")
            # フォールバック用のWebhook URL
            self.webhook_url = "https://discord.com/api/webhooks/1387373314988838940/1I64p3hITSUoToSeTOfjCLNg7QgGT9h0rdP9z2fNJASiLxJcx2S8fvoCxA-J8W_Osoiv"
    
    def load_notification_history(self):
        """通知履歴を読み込み"""
        try:
            if os.path.exists(self.notified_file):
                with open(self.notified_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"hot_days": [], "rainy_mornings": []}
        except:
            return {"hot_days": [], "rainy_mornings": []}
    
    def save_notification_history(self):
        """通知履歴を保存"""
        try:
            with open(self.notified_file, 'w', encoding='utf-8') as f:
                json.dump(self.notified_dates, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"通知履歴保存エラー: {e}")
    
    def get_weather_forecast(self, coords, days=7):
        """天気予報を取得"""
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
                "hourly": "temperature_2m,precipitation,weather_code",
                "timezone": "Asia/Tokyo",
                "forecast_days": days
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"{coords['name']} 天気予報取得エラー: {e}")
            return None
    
    def check_hot_temperature_condition(self):
        """手稲区25度超え条件をチェック"""
        data = self.get_weather_forecast(self.teine_coords)
        if not data:
            return []
        
        hot_days = []
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        
        for i in range(len(dates)):
            if i < len(temp_max) and temp_max[i] > 25:
                date_obj = datetime.fromisoformat(dates[i])
                date_str = date_obj.strftime("%Y-%m-%d")
                
                # 通知済みかチェック
                if date_str not in self.notified_dates["hot_days"]:
                    hot_days.append({
                        "date": date_str,
                        "day": date_obj.strftime("%m/%d"),
                        "weekday": self.get_weekday_jp(date_obj.weekday()),
                        "temperature": temp_max[i],
                        "location": "手稲区"
                    })
        
        return hot_days
    
    def check_rainy_morning_condition(self):
        """清田区朝8時雨条件をチェック"""
        data = self.get_weather_forecast(self.kiyota_coords)
        if not data:
            return []
        
        rainy_mornings = []
        hourly = data.get("hourly", {})
        hourly_times = hourly.get("time", [])
        hourly_precip = hourly.get("precipitation", [])
        hourly_temps = hourly.get("temperature_2m", [])
        
        # 各日の朝8時をチェック
        today = datetime.now().date()
        for day_offset in range(7):  # 7日間チェック
            target_date = today + timedelta(days=day_offset)
            target_8am = datetime.combine(target_date, datetime.min.time().replace(hour=8))
            target_8am_str = target_8am.strftime("%Y-%m-%dT%H:%M")
            
            # 最も近い時刻のデータを探す
            closest_index = None
            min_diff = float('inf')
            
            for i, time_str in enumerate(hourly_times):
                try:
                    time_obj = datetime.fromisoformat(time_str)
                    time_str_formatted = time_obj.strftime("%Y-%m-%dT%H:%M")
                    
                    if time_str_formatted == target_8am_str:
                        closest_index = i
                        break
                    
                    diff = abs((time_obj - target_8am).total_seconds())
                    if diff < min_diff and diff <= 3600:  # 1時間以内
                        min_diff = diff
                        closest_index = i
                except:
                    continue
            
            if closest_index is not None and closest_index < len(hourly_precip):
                precipitation = hourly_precip[closest_index]
                
                if precipitation > 0.1:  # 0.1mm以上の雨
                    date_str = target_date.strftime("%Y-%m-%d")
                    
                    # 通知済みかチェック
                    if date_str not in self.notified_dates["rainy_mornings"]:
                        temperature = hourly_temps[closest_index] if closest_index < len(hourly_temps) else 0
                        
                        rainy_mornings.append({
                            "date": date_str,
                            "day": target_date.strftime("%m/%d"),
                            "weekday": self.get_weekday_jp(target_date.weekday()),
                            "precipitation": precipitation,
                            "temperature": temperature,
                            "location": "清田区"
                        })
        
        return rainy_mornings
    
    def get_weekday_jp(self, weekday):
        """曜日を日本語に変換"""
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]
        return weekdays[weekday]
    
    def send_discord_notification(self, message, color=0x00ff00):
        """Discord通知を送信"""
        try:
            embed = {
                "title": "🌤️ 天気アラート",
                "description": message,
                "color": color,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "footer": {
                    "text": "Weather Alert System"
                }
            }
            
            payload = {
                "content": f"<@{self.user_discord_id}>",  # メンション通知
                "embeds": [embed]
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            print(f"✅ Discord通知送信成功: {response.status_code}")
            return True
            
        except Exception as e:
            print(f"❌ Discord通知送信エラー: {e}")
            return False
    
    def check_and_notify(self):
        """条件チェックして通知"""
        print("🔍 天気条件チェック開始...")
        print(f"⏰ チェック時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 手稲区25度超えチェック
        hot_days = self.check_hot_temperature_condition()
        
        # 清田区朝8時雨チェック  
        rainy_mornings = self.check_rainy_morning_condition()
        
        notifications_sent = 0
        
        # 暑い日の通知
        for hot_day in hot_days:
            message = f"""🔥 **手稲区 高温アラート**
📅 日付: {hot_day['day']}（{hot_day['weekday']}）
🌡️ 最高気温: **{hot_day['temperature']:.1f}°C**
📍 地域: {hot_day['location']}

⚠️ 25度を超える予報です！熱中症対策をお忘れなく。"""
            
            if self.send_discord_notification(message, color=0xff4500):  # オレンジ色
                self.notified_dates["hot_days"].append(hot_day["date"])
                notifications_sent += 1
                print(f"🔥 暑い日通知送信: {hot_day['day']} ({hot_day['temperature']:.1f}°C)")
        
        # 雨の朝の通知
        for rainy_morning in rainy_mornings:
            message = f"""☔ **清田区 朝雨アラート**
📅 日付: {rainy_morning['day']}（{rainy_morning['weekday']}）
🌧️ 朝8時頃の降水量: **{rainy_morning['precipitation']:.1f}mm**
🌡️ 気温: {rainy_morning['temperature']:.1f}°C
📍 地域: {rainy_morning['location']}

☂️ 朝の外出時は傘をお持ちください！"""
            
            if self.send_discord_notification(message, color=0x4169e1):  # 青色
                self.notified_dates["rainy_mornings"].append(rainy_morning["date"])
                notifications_sent += 1
                print(f"☔ 雨の朝通知送信: {rainy_morning['day']} ({rainy_morning['precipitation']:.1f}mm)")
        
        # 通知履歴を保存
        if notifications_sent > 0:
            self.save_notification_history()
        
        # 結果表示
        if notifications_sent == 0:
            print("📝 新しい通知条件はありませんでした")
        else:
            print(f"✅ {notifications_sent}件の通知を送信しました")
        
        # サマリー送信（1日1回）
        self.send_daily_summary_if_needed()
    
    def send_daily_summary_if_needed(self):
        """1日1回のサマリー通知"""
        today = datetime.now().strftime("%Y-%m-%d")
        summary_file = "/home/fujinosuke/daily_summary_sent.txt"
        
        # 今日既にサマリーを送信したかチェック
        last_summary_date = ""
        try:
            if os.path.exists(summary_file):
                with open(summary_file, 'r') as f:
                    last_summary_date = f.read().strip()
        except:
            pass
        
        if last_summary_date != today:
            # 今日の状況をサマリー
            hot_days = self.check_hot_temperature_condition()
            rainy_mornings = self.check_rainy_morning_condition()
            
            message = f"""📊 **本日の天気監視サマリー**
📅 日付: {datetime.now().strftime('%m/%d（%a）')}

🔥 手稲区25度超え予報: {len(hot_days)}日
☔ 清田区朝8時雨予報: {len(rainy_mornings)}日

📡 監視システム正常稼働中
🕒 次回チェック: 30分後"""
            
            if self.send_discord_notification(message, color=0x008000):  # 緑色
                try:
                    with open(summary_file, 'w') as f:
                        f.write(today)
                except:
                    pass
                print("📊 日次サマリー送信完了")
    
    def run_continuous_monitoring(self):
        """継続監視モード"""
        print("🚀 天気Discord通知システム開始")
        print("=" * 50)
        print("📡 監視条件:")
        print("  🔥 手稲区: 最高気温25度超え")
        print("  ☔ 清田区: 朝8時雨予報")
        print("⏰ チェック間隔: 30分")
        print("=" * 50)
        
        while True:
            try:
                self.check_and_notify()
                print(f"💤 次回チェックまで30分待機... (次回: {(datetime.now() + timedelta(minutes=30)).strftime('%H:%M')})")
                time.sleep(1800)  # 30分待機
                
            except KeyboardInterrupt:
                print("\n⏹️ 監視システムを停止します")
                break
            except Exception as e:
                print(f"❌ エラー発生: {e}")
                print("⏳ 5分後に再試行...")
                time.sleep(300)  # 5分待機

def main():
    """メイン実行"""
    notifier = WeatherDiscordNotifier()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # 継続監視モード
        notifier.run_continuous_monitoring()
    else:
        # 単発チェック
        notifier.check_and_notify()

if __name__ == "__main__":
    main()