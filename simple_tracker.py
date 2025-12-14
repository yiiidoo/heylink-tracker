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
        "url": "https://heylink.me/Kopilbeysponsorlar/",
        "name": "Kopilbey Sponsorlar"
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

def scrape_heylink(url, name):
    """Sayfayı scrape et ve link sıralaması değişikliklerini tespit et"""
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

        # Rastgele delay (3-7 saniye arası)
        delay = random.uniform(3, 7)
        print(f"⏳ {name}: {delay:.1f}s bekleniyor...")
        time.sleep(delay)

        # Create request
        req = urllib.request.Request(url, headers=headers)

        # Open URL
        with urllib.request.urlopen(req, timeout=45) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # Tüm linkleri çıkar (sıralama ile)
        links = []
        link_pattern = r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>([^<]*)</a>'
        matches = re.findall(link_pattern, html, re.IGNORECASE | re.DOTALL)

        for i, (href, text) in enumerate(matches, 1):
            clean_text = text.strip()
            if clean_text and len(clean_text) > 1:  # Anlamsız linkleri filtrele
                links.append({
                    'position': i,
                    'text': clean_text[:50],  # İlk 50 karakter
                    'href': href
                })

        # Link listesinin hash'i
        links_hash = hashlib.md5(str(links).encode('utf-8')).hexdigest()

        result = {
            "success": True,
            "name": name,
            "url": url,
            "links_found": len(links),
            "links": links[:10],  # İlk 10 link
            "links_hash": links_hash,
            "timestamp": datetime.now().isoformat()
        }

        # Geçmiş ile karşılaştır
        url_key = url
        if url_key in page_history:
            prev_data = page_history[url_key]
            prev_links = prev_data.get('links', [])
            prev_hash = prev_data.get('links_hash', '')

            # Link sıralaması değişikliği
            if links_hash != prev_hash:
                result["ranking_changed"] = True

                # Yeni/eksilen linkleri tespit et
                current_hrefs = {link['href'] for link in links}
                prev_hrefs = {link['href'] for link in prev_links}

                new_links = current_hrefs - prev_hrefs
                removed_links = prev_hrefs - current_hrefs

                result["new_links"] = len(new_links)
                result["removed_links"] = len(removed_links)

                if new_links or removed_links:
                    result["change_summary"] = f"🔄 Sıralama değişti! +{len(new_links)} yeni, -{len(removed_links)} çıkarıldı"
                else:
                    result["change_summary"] = "🔄 Link sırası değişti"
            else:
                result["ranking_changed"] = False
                result["change_summary"] = "✅ Sıralama değişikliği yok"
        else:
            result["first_check"] = True
            result["change_summary"] = "🆕 İlk kontrol - referans alındı"

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
    print("🤖 Heylink Tracker Başlatıldı")
    print("📊 Her 15 dakikada bir kontrol edilecek")
    print("🎯 Link sıralaması değişiklikleri takip edilecek")
    print("🌐 Replit Deployment - Sürekli Çalışacak")
    print("=" * 50)

    while True:
        try:
            # Başlangıç bildirimi
            start_msg = f"🤖 **Heylink Tracker - Kontrol Başlıyor**\n\n"
            start_msg += f"📅 {datetime.now().strftime('%H:%M:%S')}\n"
            start_msg += f"🎯 **Kopilbey Sponsorlar** sayfası kontrol ediliyor\n\n"
            start_msg += f"🔄 Her 15 dakikada bir link sıralaması kontrol edilecek"

            send_telegram_message(start_msg)

            results = []
            for heylink in HEYLINKS:
                result = scrape_heylink(heylink["url"], heylink["name"])
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
                    result_msg += f"🔗 Toplam link: {result['links_found']}\n"

                    # İlk kontrol mü?
                    if result.get("first_check"):
                        result_msg += f"🆕 İlk kontrol - sıralama kaydedildi\n"
                    else:
                        # Sıralama değişikliği
                        if result.get("ranking_changed"):
                            result_msg += f"🚨 **SIRALAMA DEĞİŞTİ!**\n"
                            result_msg += f"📊 {result.get('change_summary', 'Sıralama güncellendi')}\n"

                            # Yeni/eksilen link sayısı
                            new_count = result.get("new_links", 0)
                            removed_count = result.get("removed_links", 0)
                            if new_count > 0 or removed_count > 0:
                                result_msg += f"➕ {new_count} yeni link, ➖ {removed_count} çıkarıldı\n"

                            changes_found += 1
                        else:
                            result_msg += f"✅ {result.get('change_summary', 'Sıralama aynı')}\n"

                    # İlk 5 linki göster (değişiklik varsa)
                    if result.get("ranking_changed") or result.get("first_check"):
                        links = result.get("links", [])[:5]
                        if links:
                            result_msg += f"📋 İlk 5 link:\n"
                            for link in links:
                                result_msg += f"• {link['position']}. {link['text'][:30]}...\n"

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
