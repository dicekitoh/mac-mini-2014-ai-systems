#!/usr/bin/env python3
"""
Microsoft Graph API 再認証完了スクリプト（カレンダー権限追加）
"""

import sys
import os
sys.path.append('/home/rootmax')

from microsoft_graph_contacts import MicrosoftGraphContacts

def complete_reauth(auth_code):
    """再認証を完了"""
    print("=== Microsoft Graph 再認証完了処理 ===")
    
    graph = MicrosoftGraphContacts()
    
    print(f"\n認証コード: {auth_code[:20]}...")
    
    if graph.exchange_code_for_token(auth_code):
        print("\n✅ 再認証成功！トークンを保存しました。")
        
        # ユーザー情報を取得してテスト
        user_info = graph.get_user_info()
        if user_info:
            print(f"\nログインユーザー: {user_info.get('displayName', 'Unknown')}")
            print(f"メール: {user_info.get('mail', user_info.get('userPrincipalName', 'Unknown'))}")
            
        return True
    else:
        print("\n❌ 再認証失敗")
        return False

if __name__ == '__main__':
    # 認証コード
    auth_code = "1.AWsAP6FBVfOJJUOkRAK3-MqrCamx0CnEqU5Ok7mqlW3akJBrAO1rAA.AgABBAIAAABVrSpeuWamRam2jAF1XRQEAwDs_wUA9P981Fr0kO0V9iAYfdnmxmQerthQuAdnHPGcs7yW6GDTPWn55tzB9oljkerQWEStTdRK8cCrocsq4lBFKkbWgZ5Ev6t8bKfkKWj2JazTegMeBCMTEEQniY-Umn_HOI8mR64YqRo3MbIFuRDcfICbieLcqOq7RTIfN8xdK6CmCgPTQtz5NSBpOrF23oWOgnk8tbxjuUHp3f9_Q0J74axvnrGoBPz1VUJpL1Lx6r88mSWu1eLzx-lKj3YPCdLVWzRNjHwKhPHtHps6zYLRLahzILA5VUY8e17E2b5iFxrKrHZWTvc-ULaR3Y9uBz8-a9x3bZkiWZE-4yepBKgtDvDTBz4ngnFPHR45zEghbzu4s_AIsZguGA2v5uZdQTmoBTHlStoIRp5q0G4JPjPuGZRbENN6gq6EOLUAIx0ZUiSPngsiTQ01vv0X8gmhDQaJSTe-Jp-ABoRZNYAJGJPPZKA2elEa745UWQs7lNaVHM0L5uQ8UBoaM9JYrzzMhwvYhw6MWhLYTLlyCLsF1oUw5nBRJUlKKmZDZ9jehaVZHlKuyv_vuRzOjLOv01MvolRLr0m5LRaLLmwvY5jT7UR00kc6HXUPwUmfZxMOe965E7jz6UX396G5jvrw8UtKFbZJvJaHxlTkNoVK8rspKHR0wEnM23H5HYy1tl-B_FYIEX8OLNZNdiisp0EBlDrX8xALjxIrlV5ain7Ax4GyDJaxrxKuUQreBg_334qxQfHd8YkNgMJSzYrEEGXPVkAU2Y1sIr3bayYVIepeGbwr324oB04AeYWQGD6XMp7TvLzItG1B4rv-ehGg77cyiglT"
    
    complete_reauth(auth_code)