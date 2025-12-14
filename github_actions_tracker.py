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
import requests

# Selenium imports (GitHub Actions için)
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Environment variables'dan oku
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Global geçmiş (GitHub Actions'ta persist etmez ama basit için OK)
page_history = {}

# Ücretsiz proxy listesi (güncellenebilir)
PROXY_LIST = [
    {'http': 'http://51.159.115.233:3128', 'https': 'http://51.159.115.233:3128'},
    {'http': 'http://20.205.61.143:3128', 'https': 'http://20.205.61.143:3128'},
    {'http': 'http://103.151.177.106:8080', 'https': 'http://103.151.177.106:8080'},
    {'http': 'http://185.82.99.181:9091', 'https': 'http://185.82.99.181:9091'},
    {'http': 'http://190.97.226.236:999', 'https': 'http://190.97.226.236:999'},
    {'http': 'http://181.78.22.52:999', 'https': 'http://181.78.22.52:999'},
    {'http': 'http://45.70.236.194:999', 'https': 'http://45.70.236.194:999'},
    {'http': 'http://200.105.215.18:33630', 'https': 'http://200.105.215.18:33630'},
    {'http': 'http://190.103.177.131:80', 'https': 'http://190.103.177.131:80'},
    {'http': 'http://181.78.22.150:999', 'https': 'http://181.78.22.150:999'}
]

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
            delay = random.uniform(15, 30)  # Heylink için çok uzun delay
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

        # Heylink için Selenium kullan (eğer mevcutsa)
        if 'heylink' in url.lower() and SELENIUM_AVAILABLE:
            print(f"🤖 {name}: Selenium ile Cloudflare bypass deneniyor...")
            try:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')

                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                driver.get(url)

                # Sayfa yüklenene kadar bekle
                time.sleep(5)
                html = driver.page_source
                driver.quit()

                print(f"✅ {name}: Selenium başarılı!")

            except Exception as selenium_error:
                print(f"⚠️ {name}: Selenium başarısız ({selenium_error}), proxy ile requests deneniyor...")
                # Selenium başarısız olursa proxy ile requests dene
                try:
                    proxy = random.choice(PROXY_LIST)
                    response = requests.get(url, headers=headers, proxies=proxy, timeout=30)
                    response.raise_for_status()
                    html = response.text
                    print(f"✅ {name}: Proxy başarılı!")
                except Exception as proxy_error:
                    print(f"⚠️ {name}: Proxy de başarısız ({proxy_error}), normal yöntem deneniyor...")
                    # Her şey başarısız olursa normal urllib kullan
                    with urllib.request.urlopen(req, timeout=60) as response:
                        html = response.read().decode('utf-8', errors='ignore')
        else:
            # Normal siteler için urllib kullan
            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8', errors='ignore')

        # Linkleri çıkar (daha geniş pattern)
        links = []
        # Farklı link pattern'leri dene (sadece href yakala)
        patterns = [
            r'href=["\']([^"\']*)["\']',  # Tüm href attribute'ları
        ]

        all_matches = []
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            all_matches.extend(matches)

        # Link text'lerini de yakala (ayrı arama)
        text_pattern = r'<a[^>]*href=["\'][^"\']*["\'][^>]*>([^<]*)</a>'
        text_matches = re.findall(text_pattern, html, re.IGNORECASE | re.DOTALL)

        # Benzersiz linkler için set kullan
        seen_hrefs = set()
        for i, href in enumerate(all_matches):
            # Geçerli link kontrolü
            if href and not href.startswith(('javascript:', 'mailto:', '#', 'tel:')):
                # Temizleme
                clean_href = href.strip()

                # Text'i eşleştir (varsa)
                text = ""
                if i < len(text_matches):
                    text = text_matches[i].strip()[:50]

                if not text:
                    text = clean_href[:50]

                # Benzersiz kontrol
                if clean_href not in seen_hrefs and len(clean_href) > 5:
                    links.append({
                        'position': len(links) + 1,
                        'text': text,
                        'href': clean_href
                    })
                    seen_hrefs.add(clean_href)

                    # Maksimum 20 link ile sınırla
                    if len(links) >= 20:
                        break

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
