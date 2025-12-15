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
import ssl
from bs4 import BeautifulSoup
import cloudscraper
from fake_useragent import UserAgent

# Selenium imports (GitHub Actions için)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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
        # Fake user agent oluşturucu
        ua = UserAgent()

        # Heylink için çok uzun delay (Cloudflare bypass için)
        if 'heylink' in url.lower():
            delay = random.uniform(20, 35)
        else:
            delay = random.uniform(5, 10)

        print(f"⏳ {name}: {delay:.1f}s bekleniyor...")
        time.sleep(delay)

        # Cloudscraper ile güçlü Cloudflare bypass
        print(f"🔥 {name}: Cloudscraper ile Cloudflare bypass başlatılıyor...")
        try:
            # cloudscraper ile Cloudflare bypass
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            response = scraper.get(url, timeout=60)

            if response.status_code == 200:
                html = response.text
                print(f"✅ {name}: Cloudscraper başarılı!")
            else:
                raise Exception(f"HTTP {response.status_code}")

        except Exception as cf_error:
            print(f"⚠️ {name}: Cloudscraper başarısız ({cf_error}), Selenium deneniyor...")
            try:
                # Selenium fallback
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument(f'--user-agent={ua.random}')

                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

                # Webdriver detection bypass
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                driver.get(url)
                time.sleep(15)

                html = driver.page_source
                driver.quit()

                print(f"✅ {name}: Selenium başarılı!")

            except Exception as selenium_error:
                print(f"❌ {name}: Tüm yöntemler başarısız - {selenium_error}")
                raise Exception("Tüm bypass yöntemleri başarısız")
        # Debug: Save HTML to file for inspection
        with open("heylink_content.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("heylink_content.html dosyasına kaydedildi.")

        def parse_links_from_html(page_html):
            """Heylink sayfasındaki sponsor linklerini çıkar."""
            parsed_links = []
            soup = BeautifulSoup(page_html, "html.parser")
            cards = soup.select("div.preview-link-item__component a.preview-link-wrapper")
            for idx, card in enumerate(cards, start=1):
                href = card.get("href", "").strip()
                if not href or href.startswith(("javascript:", "mailto:", "#", "tel:")):
                    continue
                name_el = card.select_one(".link-info .name")
                text = name_el.get_text(strip=True) if name_el else card.get_text(strip=True)
                if not text:
                    text = href
                parsed_links.append(
                    {
                        "position": idx,
                        "text": text[:120],
                        "href": href,
                    }
                )
            return parsed_links

        # Linkleri çıkar (BeautifulSoup ile öncelikli, regex yedekli)
        links = parse_links_from_html(html)
        link_count = len(links)

        if not links:
            try:
                # Tüm link tag'larını say (yedek)
                link_count = len(re.findall(r'<a[^>]*href[^>]*>.*?</a>', html, re.IGNORECASE | re.DOTALL))
                link_matches = re.findall(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>', html, re.IGNORECASE | re.DOTALL)

                for i, (href, text) in enumerate(link_matches[:5]):  # Sadece ilk 5
                    if href and not href.startswith(('javascript:', 'mailto:', '#', 'tel:')):
                        clean_text = text.strip()[:120] if text.strip() else href[:120]
                        links.append({
                            'position': i + 1,
                            'text': clean_text,
                            'href': href
                        })

                if not links:
                    for i in range(min(3, link_count)):  # En fazla 3 boş link
                        links.append({
                            'position': i + 1,
                            'text': f'Link {i+1}',
                            'href': f'#link{i+1}'
                        })
            except Exception as parse_error:
                print(f"⚠️ Link parsing hatası: {parse_error}")
                link_count = len(links)


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
