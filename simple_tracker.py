#!/usr/bin/env python3
"""
Basit Heylink Takip Sistemi - Local Çalışır (Built-in modules only)
"""

import urllib.request
import urllib.parse
import json
import time
import re
import random
from datetime import datetime

# Config
TELEGRAM_BOT_TOKEN = "7795627429:AAHdzjkww7WEUSXRsgG38rHMre4bMFG4mpw"
TELEGRAM_CHAT_ID = "7155382465"

HEYLINKS = [
    {
        "url": "https://heylink.me/sorunsuz",
        "name": "Sorunsuz Ana Sayfa"
    },
    {
        "url": "https://heylink.me/GuvenilirBahisSitelerimiz/",
        "name": "Güvenilir Bahis Siteleri"
    },
    {
        "url": "https://httpbin.org/html",
        "name": "Test Sayfası (httpbin.org)"
    },
    {
        "url": "https://www.google.com",
        "name": "Google (test)"
    }
]

def send_telegram_message(message):
    """Telegram'a mesaj gönder (urllib ile)"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }

        # URL encode data
        data = urllib.parse.urlencode(data).encode('utf-8')

        # POST request
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        print(f"Telegram hatası: {e}")
        return False

def scrape_heylink(url, name):
    """Sayfayı scrape et (urllib ile)"""
    try:
        # Rastgele User-Agent seçimi
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]

        # Daha gelişmiş bot-karşıtı headers
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Referer': 'https://www.google.com/'
        }

        # Rastgele delay (1-3 saniye)
        time.sleep(random.uniform(1, 3))

        # Create request
        req = urllib.request.Request(url, headers=headers)

        # Open URL
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # Count links (simple regex)
        link_count = len(re.findall(r'<a[^>]*href[^>]*>.*?</a>', html, re.IGNORECASE))

        return {
            "success": True,
            "name": name,
            "url": url,
            "links_found": link_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "name": name,
            "url": url,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    print("🤖 Heylink Tracker Başlatıldı")
    print("📊 Her 5 dakikada bir kontrol edilecek")
    print("=" * 50)

    while True:
        try:
            # Başlangıç bildirimi
            start_msg = f"🤖 **Heylink Tracker - Kontrol Başlıyor**\n\n"
            start_msg += f"📅 {datetime.now().strftime('%H:%M:%S')}\n"
            start_msg += f"📊 {len(HEYLINKS)} sayfa kontrol ediliyor\n\n"
            start_msg += f"🔄 Her 5 dakikada bir kontrol ediliyor"

            send_telegram_message(start_msg)

            results = []
            for heylink in HEYLINKS:
                result = scrape_heylink(heylink["url"], heylink["name"])
                results.append(result)
                print(f"✅ {result['name']}: {'Başarılı' if result['success'] else 'Hata'}")

                if not result["success"]:
                    print(f"   ❌ {result['error']}")

            # Sonuç bildirimi
            result_msg = f"🤖 **Heylink Tracker - Kontrol Tamamlandı**\n\n"
            result_msg += f"📅 {datetime.now().strftime('%H:%M:%S')}\n"

            successful = sum(1 for r in results if r["success"])
            errors = len(results) - successful

            result_msg += f"📊 {len(results)} sayfa kontrol edildi\n"
            result_msg += f"✅ {successful} başarılı\n"

            if errors > 0:
                result_msg += f"❌ {errors} hata\n"

            for result in results:
                if result["success"]:
                    result_msg += f"• {result['name']}: {result['links_found']} link\n"
                else:
                    result_msg += f"• {result['name']}: Hata\n"

            result_msg += f"\n🔄 5 dakika sonra tekrar kontrol edilecek"

            send_telegram_message(result_msg)

            print(f"✅ Kontrol tamamlandı - {successful}/{len(results)} başarılı")
            print("⏰ 5 dakika bekleniyor...")
            print("-" * 50)

            time.sleep(300)  # 5 dakika

        except KeyboardInterrupt:
            print("\n🛑 Sistem durduruldu")
            break
        except Exception as e:
            print(f"❌ Sistem hatası: {e}")
            time.sleep(60)  # Hata durumunda 1 dakika bekle

if __name__ == "__main__":
    main()
