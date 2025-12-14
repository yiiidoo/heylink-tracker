import json
import os
import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import telegram
from telegram.error import TelegramError

# Vercel KV için (alternatif olarak JSON dosyaları kullanacağız)
DATA_STORE = {}

def load_config():
    """Environment variables'dan config yükle"""
    return {
        "telegram": {
            "bot_token": os.environ.get("TELEGRAM_BOT_TOKEN", ""),
            "chat_ids": os.environ.get("TELEGRAM_CHAT_IDS", "").split(",") if os.environ.get("TELEGRAM_CHAT_IDS") else [],
            "notification_interval": 300
        },
        "heylinks": [
            {
                "id": "sorunsuz",
                "url": "https://heylink.me/sorunsuz",
                "name": "Sorunsuz Ana Sayfa",
                "check_interval": 300,
                "track_keywords": ["volacasinonun"]
            }
            # İlk başta sadece 1-2 sayfa ile test edelim
        ],
        "settings": {
            "max_concurrent_requests": 5,  # Vercel limitleri için düşük
            "request_timeout": 20,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "enable_logging": True
        }
    }

def get_page_hash(content):
    """Sayfa içeriğinin hash'ini al"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def scrape_heylink(heylink):
    """Tek bir heylink sayfasını scrape et"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(heylink['url'], headers=headers, timeout=20)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Sayfa başlığını al
        title = soup.title.string if soup.title else "Başlık bulunamadı"

        # Tüm linkleri topla
        links = []
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True)
            if link_text and len(link_text) > 2:  # Çok kısa linkleri atla
                links.append({
                    'text': link_text,
                    'href': link['href'],
                    'position': len(links) + 1
                })

        # Sayfa hash'i
        page_hash = get_page_hash(str(links))

        return {
            'id': heylink['id'],
            'url': heylink['url'],
            'name': heylink['name'],
            'title': title,
            'links': links,
            'hash': page_hash,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }

    except Exception as e:
        return {
            'id': heylink['id'],
            'url': heylink['url'],
            'name': heylink['name'],
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

def find_changes(current_data, previous_data):
    """İki veri seti arasındaki değişiklikleri bul"""
    if not previous_data or previous_data.get('status') == 'error':
        return None

    changes = {
        'new_links': [],
        'removed_links': [],
        'position_changes': []
    }

    # Hash karşılaştırması
    if current_data['hash'] != previous_data['hash']:
        changes['hash_changed'] = True

        # Link karşılaştırması
        current_links = {link['href']: link for link in current_data['links']}
        previous_links = {link['href']: link for link in previous_data['links']}

        # Yeni linkler
        for href, link in current_links.items():
            if href not in previous_links:
                changes['new_links'].append(link)

        # Silinen linkler
        for href, link in previous_links.items():
            if href not in current_links:
                changes['removed_links'].append(link)

        # Pozisyon değişiklikleri (sadece önemli olanlar)
        for href, current_link in current_links.items():
            if href in previous_links:
                prev_link = previous_links[href]
                if abs(current_link['position'] - prev_link['position']) >= 3:  # 3+ sıra değişimi
                    changes['position_changes'].append({
                        'link': current_link['text'],
                        'old_position': prev_link['position'],
                        'new_position': current_link['position']
                    })

    return changes if any(changes.values()) else None

def send_telegram_notification(heylink_data, changes):
    """Telegram'a bildirim gönder"""
    try:
        config = load_config()
        bot_token = config['telegram']['bot_token']
        chat_ids = config['telegram']['chat_ids']

        if not bot_token or not chat_ids:
            print("Telegram config eksik")
            return

        bot = telegram.Bot(token=bot_token)

        message = f"🔄 **{heylink_data['name']}** - Değişiklik Algılandı!\n\n"
        message += f"📅 {datetime.now().strftime('%H:%M:%S')}\n"
        message += f"🔗 {heylink_data['url']}\n\n"

        if changes.get('new_links'):
            message += f"🆕 **Yeni Linkler ({len(changes['new_links'])}):**\n"
            for link in changes['new_links'][:3]:  # İlk 3 taneyi göster
                message += f"• {link['text']}\n"
            message += "\n"

        if changes.get('removed_links'):
            message += f"❌ **Silinen Linkler ({len(changes['removed_links'])}):**\n"
            for link in changes['removed_links'][:3]:
                message += f"• {link['text']}\n"
            message += "\n"

        if changes.get('position_changes'):
            message += f"📊 **Önemli Pozisyon Değişiklikleri ({len(changes['position_changes'])}):**\n"
            for change in changes['position_changes'][:5]:
                direction = "⬆️" if change['new_position'] < change['old_position'] else "⬇️"
                message += f"{direction} {change['link']}: {change['old_position']} → {change['new_position']}\n"
            message += "\n"

        # Tüm chat ID'lerine gönder
        for chat_id in chat_ids:
            if chat_id.strip():
                try:
                    bot.send_message(
                        chat_id=chat_id.strip(),
                        text=message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    print(f"Bildirim gönderildi: {chat_id}")
                except TelegramError as e:
                    print(f"Telegram hatası {chat_id}: {str(e)}")

    except Exception as e:
        print(f"Bildirim gönderme hatası: {str(e)}")

def check_all_heylinks():
    """Tüm heylink'leri kontrol et"""
    config = load_config()
    heylinks = config['heylinks']

    print(f"🔍 {len(heylinks)} sayfa kontrol ediliyor...")

    changes_found = 0

    for heylink in heylinks:
        try:
            print(f"Kontrol ediliyor: {heylink['name']}")

            # Mevcut veriyi çek
            current_data = scrape_heylink(heylink)

            if current_data['status'] == 'success':
                # Önceki veriyi al (Vercel KV veya global dict)
                previous_data = DATA_STORE.get(heylink['id'])

                # Değişiklikleri kontrol et
                changes = find_changes(current_data, previous_data)

                if changes:
                    changes_found += 1
                    print(f"✨ Değişiklik: {heylink['name']}")

                    # Bildirim gönder
                    send_telegram_notification(current_data, changes)

                # Yeni veriyi sakla
                DATA_STORE[heylink['id']] = current_data

            else:
                print(f"❌ Hata: {heylink['name']} - {current_data['error']}")

        except Exception as e:
            print(f"İşlem hatası {heylink['name']}: {str(e)}")

    print(f"✅ Kontrol tamamlandı! {changes_found} değişiklik bulundu.")
    return changes_found

def handler(request):
    """Vercel serverless function handler"""
    try:
        # Sadece POST isteklerini kabul et (cron job'lar için)
        if request.method != 'POST':
            return {
                'statusCode': 405,
                'body': json.dumps({'error': 'Method not allowed'})
            }

        # Sistem kontrolünü başlat
        changes_found = check_all_heylinks()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'success',
                'message': f'Kontrol tamamlandı, {changes_found} değişiklik bulundu',
                'timestamp': datetime.now().isoformat()
            })
        }

    except Exception as e:
        print(f"Handler hatası: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

# Vercel için ana fonksiyon
def main(request, response):
    """Vercel Python runtime için main function"""
    result = handler(request)

    response.status_code = result['statusCode']
    response.headers['Content-Type'] = 'application/json'
    response.body = result['body']

    return response

# Test için direkt çalıştırma
if __name__ == "__main__":
    print("🧪 Vercel function testi...")
    check_all_heylinks()
