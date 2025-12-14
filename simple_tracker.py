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
import hashlib
from datetime import datetime

# Config
TELEGRAM_BOT_TOKEN = "7795627429:AAHdzjkww7WEUSXRsgG38rHMre4bMFG4mpw"
TELEGRAM_CHAT_ID = "7155382465"

HEYLINKS = [
    {
        "url": "https://heylink.me/sorunsuz",
        "name": "Sorunsuz Ana Sayfa",
        "track_keywords": ["volacasinonun"]  # Özel kelimeler
    },
    {
        "url": "https://heylink.me/GuvenilirBahisSitelerimiz/",
        "name": "Güvenilir Bahis Siteleri",
        "track_keywords": ["casino", "bahis"]  # Özel kelimeler
    },
    {
        "url": "https://httpbin.org/html",
        "name": "Test Sayfası (httpbin.org)",
        "track_keywords": []
    },
    {
        "url": "https://www.google.com",
        "name": "Google (test)",
        "track_keywords": []
    }
]

# Sayfa geçmişini tut (hash karşılaştırması için)
page_history = {}

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

def scrape_heylink(url, name, track_keywords=None):
    """Sayfayı scrape et ve değişiklikleri tespit et"""
    if track_keywords is None:
        track_keywords = []

    try:
        # Çok gelişmiş bot-karşıtı headers
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]

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
            'Referer': 'https://www.google.com/',
            'Cookie': ''  # Boş cookie
        }

        # Rastgele delay (2-5 saniye arası)
        delay = random.uniform(2, 5)
        print(f"⏳ {name}: {delay:.1f}s bekleniyor...")
        time.sleep(delay)

        # Create request
        req = urllib.request.Request(url, headers=headers)

        # Open URL
        with urllib.request.urlopen(req, timeout=45) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # Sayfa hash'i oluştur
        page_hash = hashlib.md5(html.encode('utf-8')).hexdigest()

        # Link sayısı
        link_count = len(re.findall(r'<a[^>]*href[^>]*>.*?</a>', html, re.IGNORECASE))

        # Özel kelimeler kontrolü
        keyword_changes = {}
        if track_keywords:
            for keyword in track_keywords:
                count = html.lower().count(keyword.lower())
                keyword_changes[keyword] = count

        result = {
            "success": True,
            "name": name,
            "url": url,
            "links_found": link_count,
            "page_hash": page_hash,
            "keyword_counts": keyword_changes,
            "html_length": len(html),
            "timestamp": datetime.now().isoformat()
        }

        # Geçmiş ile karşılaştır
        url_key = url
        if url_key in page_history:
            prev_data = page_history[url_key]

            # Hash değişikliği
            if prev_data['page_hash'] != page_hash:
                result["hash_changed"] = True
                result["hash_diff"] = "Sayfa içeriği değişti"
            else:
                result["hash_changed"] = False
                result["hash_diff"] = "Değişiklik yok"

            # Özel kelime değişiklikleri
            if track_keywords:
                keyword_diffs = {}
                for keyword in track_keywords:
                    prev_count = prev_data.get('keyword_counts', {}).get(keyword, 0)
                    curr_count = keyword_changes.get(keyword, 0)
                    if prev_count != curr_count:
                        keyword_diffs[keyword] = f"{prev_count} → {curr_count}"

                if keyword_diffs:
                    result["keyword_changes"] = keyword_diffs
        else:
            result["first_check"] = True

        # Geçmişi güncelle
        page_history[url_key] = {
            'page_hash': page_hash,
            'keyword_counts': keyword_changes,
            'timestamp': result['timestamp']
        }

        return result

    except Exception as e:
        print(f"❌ {name}: Hata - {str(e)}")
        return {
            "success": False,
            "name": name,
            "url": url,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    print("🤖 Heylink Tracker Başlatıldı")
    print("📊 Her 15 dakikada bir kontrol edilecek")
    print("🎯 Sayfa değişiklikleri ve özel kelimeler takip edilecek")
    print("=" * 50)

    while True:
        try:
            # Başlangıç bildirimi
            start_msg = f"🤖 **Heylink Tracker - Kontrol Başlıyor**\n\n"
            start_msg += f"📅 {datetime.now().strftime('%H:%M:%S')}\n"
            start_msg += f"📊 {len(HEYLINKS)} sayfa kontrol ediliyor\n\n"
            start_msg += f"🔄 Her 15 dakikada bir kontrol ediliyor\n"
            start_msg += f"🎯 Sayfa içeriği ve özel kelimeler takip ediliyor"

            send_telegram_message(start_msg)

            results = []
            for heylink in HEYLINKS:
                track_keywords = heylink.get("track_keywords", [])
                result = scrape_heylink(heylink["url"], heylink["name"], track_keywords)
                results.append(result)
                print(f"✅ {result['name']}: {'Başarılı' if result['success'] else 'Hata'}")

                if not result["success"]:
                    print(f"   ❌ {result['error']}")

            # Detaylı sonuç bildirimi
            result_msg = f"🤖 **Heylink Tracker - Detaylı Rapor**\n\n"
            result_msg += f"📅 {datetime.now().strftime('%H:%M:%S')}\n\n"

            successful = sum(1 for r in results if r["success"])
            errors = len(results) - successful
            changes_found = 0

            result_msg += f"📊 **Genel Durum:**\n"
            result_msg += f"✅ {successful} başarılı\n"
            if errors > 0:
                result_msg += f"❌ {errors} hata\n"
            result_msg += "\n"

            # Detaylı rapor
            for result in results:
                result_msg += f"🔍 **{result['name']}**\n"

                if result["success"]:
                    result_msg += f"✅ Erişim: Başarılı\n"
                    result_msg += f"🔗 Link sayısı: {result['links_found']}\n"
                    result_msg += f"📄 Sayfa boyutu: {result.get('html_length', 0)} karakter\n"

                    # İlk kontrol mü?
                    if result.get("first_check"):
                        result_msg += f"🆕 İlk kontrol - referans alındı\n"
                    else:
                        # Hash değişikliği
                        if result.get("hash_changed"):
                            result_msg += f"⚡ **DEĞİŞİKLİK TESPİT EDİLDİ!**\n"
                            result_msg += f"📝 {result.get('hash_diff', 'İçerik değişti')}\n"
                            changes_found += 1
                        else:
                            result_msg += f"✅ {result.get('hash_diff', 'Değişiklik yok')}\n"

                        # Keyword değişiklikleri
                        keyword_changes = result.get("keyword_changes", {})
                        if keyword_changes:
                            result_msg += f"🏷️ **Kelime Değişiklikleri:**\n"
                            for keyword, change in keyword_changes.items():
                                result_msg += f"• '{keyword}': {change}\n"
                            changes_found += 1

                    # Özel kelime sayıları
                    keyword_counts = result.get("keyword_counts", {})
                    if keyword_counts:
                        result_msg += f"🔍 Takip edilen kelimeler: "
                        keyword_list = [f"{k}({v})" for k, v in keyword_counts.items()]
                        result_msg += ", ".join(keyword_list) + "\n"

                else:
                    result_msg += f"❌ Erişim: Başarısız\n"
                    result_msg += f"⚠️ Hata: {result.get('error', 'Bilinmiyor')[:100]}...\n"

                result_msg += "\n"

            # Özet
            result_msg += f"🎯 **Özet:**\n"
            if changes_found > 0:
                result_msg += f"🚨 **{changes_found} DEĞİŞİKLİK** tespit edildi!\n"
            else:
                result_msg += f"✅ Tüm sayfalarda değişiklik yok\n"

            result_msg += f"🔄 15 dakika sonra tekrar kontrol edilecek"

            send_telegram_message(result_msg)

            print(f"✅ Kontrol tamamlandı - {successful}/{len(results)} başarılı")
            print("⏰ 15 dakika bekleniyor...")
            print("-" * 50)

            time.sleep(900)  # 15 dakika

        except KeyboardInterrupt:
            print("\n🛑 Sistem durduruldu")
            break
        except Exception as e:
            print(f"❌ Sistem hatası: {e}")
            time.sleep(60)  # Hata durumunda 1 dakika bekle

if __name__ == "__main__":
    main()
