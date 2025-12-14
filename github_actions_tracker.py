#!/usr/bin/env python3
"""
GitHub Actions için Tek Kontrol Scripti
"""

import urllib.request
import urllib.parse
import json
import re
import random
import hashlib
import time
import os
from datetime import datetime

# Environment variables'dan oku
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Global geçmiş (GitHub Actions'ta persist etmez ama basit için OK)
page_history = {}

HEYLINKS = [
    {
        "url": "https://heylink.me/Kopilbeysponsorlar/",
        "name": "Kopilbey Sponsorlar"
    }
]

def send_telegram_message(message):
    """Telegram mesajı gönder"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram config eksik")
        return

    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }

        data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=10) as response:
            print("✅ Telegram mesajı gönderildi")
    except Exception as e:
        print(f"❌ Telegram hatası: {e}")

def scrape_heylink(url, name):
    """Sayfayı scrape et ve link sıralaması değişikliklerini tespit et"""
    try:
        # Bot-karşıtı headers
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]

        # Heylink için Cloudflare bypass headers
        if 'heylink' in url.lower():
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
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Referer': 'https://www.google.com/search?q=heylink',
                'CF-RAY': 'dummy-ray-id',
                'CF-Visitor': '{"scheme":"https"}'
            }
            delay = random.uniform(10, 20)  # Heylink için uzun delay
        else:
            # Normal siteler için
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
                'Cookie': ''
            }
            delay = random.uniform(3, 7)  # Normal delay

        print(f"⏳ {name}: {delay:.1f}s bekleniyor...")
        time.sleep(delay)

        # Request
        req = urllib.request.Request(url, headers=headers)
        # Open URL (Heylink için uzun timeout)
        timeout_val = 60 if 'heylink' in url.lower() else 30
        with urllib.request.urlopen(req, timeout=timeout_val) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # Linkleri çıkar
        links = []
        link_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>'
        matches = re.findall(link_pattern, html, re.IGNORECASE | re.DOTALL)

        for i, (href, text) in enumerate(matches, 1):
            clean_text = text.strip()
            if clean_text and len(clean_text) > 1:
                links.append({
                    'position': i,
                    'text': clean_text[:50],
                    'href': href
                })

        # Link listesinin hash'i
        links_hash = hashlib.md5(str(links).encode('utf-8')).hexdigest()

        result = {
            "success": True,
            "name": name,
            "url": url,
            "links_found": len(links),
            "links": links[:10],
            "links_hash": links_hash,
            "timestamp": datetime.now().isoformat()
        }

        # Geçmiş ile karşılaştır
        url_key = url
        if url_key in page_history:
            prev_data = page_history[url_key]
            prev_hash = prev_data.get('links_hash', '')

            if links_hash != prev_hash:
                result["ranking_changed"] = True
                result["change_summary"] = "🔄 Link sıralaması değişti"
            else:
                result["ranking_changed"] = False
                result["change_summary"] = "✅ Link sıralaması aynı"
        else:
            result["first_check"] = True
            result["change_summary"] = "🆕 İlk kontrol - referans kaydedildi"

        # Geçmişi güncelle
        page_history[url_key] = {
            'links': links,
            'links_hash': links_hash,
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
    print("🤖 GitHub Actions - Heylink Tracker")
    print("📊 Tek kontrol başlatılıyor...")
    print("=" * 50)

    # Başlangıç bildirimi
    start_msg = "🤖 **GitHub Actions - Kontrol Başlıyor**\n\n"
    start_msg += f"📅 {datetime.now().strftime('%H:%M:%S')}\n"
    start_msg += f"🎯 **Kopilbey Sponsorlar** sayfası kontrol ediliyor\n\n"
    start_msg += f"🔄 Her 15 dakikada bir link sıralaması kontrol edilecek"

    send_telegram_message(start_msg)

    results = []
    for heylink in HEYLINKS:
        result = scrape_heylink(heylink["url"], heylink["name"])
        results.append(result)

    # Detaylı rapor
    result_msg = f"🤖 **GitHub Actions - Kontrol Tamamlandı**\n\n"
    result_msg += f"📅 {datetime.now().strftime('%H:%M:%S')}\n\n"

    successful = sum(1 for r in results if r["success"])
    errors = len(results) - successful
    changes_found = 0

    result_msg += f"📊 **Genel Durum:**\n"
    result_msg += f"✅ {successful} başarılı\n"
    if errors > 0:
        result_msg += f"❌ {errors} hata\n"
    result_msg += "\n"

    for result in results:
        result_msg += f"🔍 **{result['name']}**\n"

        if result["success"]:
            result_msg += f"✅ Erişim: Başarılı\n"
            result_msg += f"🔗 Toplam link: {result['links_found']}\n"

            if result.get("first_check"):
                result_msg += f"🆕 İlk kontrol - sıralama kaydedildi\n"
            else:
                if result.get("ranking_changed"):
                    result_msg += f"🚨 **SIRALAMA DEĞİŞTİ!**\n"
                    result_msg += f"📊 {result.get('change_summary', 'Sıralama güncellendi')}\n"
                    changes_found += 1
                else:
                    result_msg += f"✅ {result.get('change_summary', 'Sıralama aynı')}\n"

            # İlk 3 linki göster
            links = result.get("links", [])[:3]
            if links:
                result_msg += f"📋 İlk 3 link:\n"
                for link in links:
                    result_msg += f"• {link['position']}. {link['text'][:30]}...\n"

        else:
            result_msg += f"❌ Erişim: Başarısız\n"
            result_msg += f"⚠️ Hata: {result.get('error', 'Bilinmiyor')[:100]}...\n"

        result_msg += "\n"

    # Özet
    result_msg += f"🎯 **Özet:**\n"
    if changes_found > 0:
        result_msg += f"🚨 **SIRALAMA DEĞİŞTİ!**\n"
        result_msg += f"🔄 Kopilbey Sponsorlar sayfasında link sıralaması güncellendi!\n"
    else:
        result_msg += f"✅ Kopilbey Sponsorlar sayfasında değişiklik yok\n"

    send_telegram_message(result_msg)

    print(f"✅ Kontrol tamamlandı - {successful}/{len(results)} başarılı")

if __name__ == "__main__":
    main()
