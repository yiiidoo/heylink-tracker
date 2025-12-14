#!/usr/bin/env python3
"""
Heylink Tracker - 100 Sayfayı Takip Eden Sistem
Telegram bot ile bildirim gönderir
"""

import json
import os
import time
import hashlib
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import telegram
from telegram.error import TelegramError

class HeylinkTracker:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.config = self.load_config()
        self.setup_logging()
        self.setup_directories()

        # Telegram bot setup
        self.bot = telegram.Bot(token=self.config['telegram']['bot_token'])
        self.chat_ids = self.config['telegram']['chat_ids']

        # Session for requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config['settings']['user_agent']
        })

        print(f"🚀 Heylink Tracker başlatıldı! {len(self.config['heylinks'])} sayfa takip ediliyor.")

    def load_config(self):
        """Config dosyasını yükle"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def setup_logging(self):
        """Logging ayarları"""
        if self.config['settings']['enable_logging']:
            log_dir = self.config['settings']['log_directory']
            os.makedirs(log_dir, exist_ok=True)

            logging.basicConfig(
                filename=os.path.join(log_dir, f'heylink_tracker_{datetime.now().strftime("%Y%m%d")}.log'),
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )

        self.logger = logging.getLogger(__name__)

    def setup_directories(self):
        """Gerekli klasörleri oluştur"""
        data_dir = self.config['settings']['data_directory']
        os.makedirs(data_dir, exist_ok=True)

    def get_page_hash(self, content):
        """Sayfa içeriğinin hash'ini al"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def scrape_heylink(self, heylink):
        """Tek bir heylink sayfasını scrape et"""
        try:
            self.logger.info(f"Scraping: {heylink['name']} - {heylink['url']}")

            response = self.session.get(
                heylink['url'],
                timeout=self.config['settings']['request_timeout']
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Sayfa başlığını al
            title = soup.title.string if soup.title else "Başlık bulunamadı"

            # Tüm linkleri topla
            links = []
            for link in soup.find_all('a', href=True):
                link_text = link.get_text(strip=True)
                if link_text:  # Boş linkleri atla
                    links.append({
                        'text': link_text,
                        'href': link['href'],
                        'position': len(links) + 1
                    })

            # Sayfa hash'i
            page_hash = self.get_page_hash(str(links))

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
            self.logger.error(f"Hata {heylink['url']}: {str(e)}")
            return {
                'id': heylink['id'],
                'url': heylink['url'],
                'name': heylink['name'],
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def load_previous_data(self, heylink_id):
        """Önceki veriyi yükle"""
        data_file = os.path.join(self.config['settings']['data_directory'], f'{heylink_id}.json')

        if os.path.exists(data_file):
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Önceki veri yüklenemedi {heylink_id}: {str(e)}")

        return None

    def save_data(self, data):
        """Veriyi kaydet"""
        data_file = os.path.join(self.config['settings']['data_directory'], f'{data["id"]}.json')

        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Veri kaydedilemedi {data['id']}: {str(e)}")

    def find_changes(self, current_data, previous_data):
        """İki veri seti arasındaki değişiklikleri bul"""
        if not previous_data or previous_data.get('status') == 'error':
            return None

        changes = {
            'new_links': [],
            'removed_links': [],
            'position_changes': [],
            'keyword_changes': []
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

            # Pozisyon değişiklikleri
            for href, current_link in current_links.items():
                if href in previous_links:
                    prev_link = previous_links[href]
                    if current_link['position'] != prev_link['position']:
                        changes['position_changes'].append({
                            'link': current_link['text'],
                            'old_position': prev_link['position'],
                            'new_position': current_link['position']
                        })

            # Anahtar kelime takibi
            heylink_config = next((h for h in self.config['heylinks'] if h['id'] == current_data['id']), None)
            if heylink_config and 'track_keywords' in heylink_config:
                for keyword in heylink_config['track_keywords']:
                    current_positions = [link for link in current_data['links'] if keyword.lower() in link['text'].lower()]
                    previous_positions = [link for link in previous_data['links'] if keyword.lower() in link['text'].lower()]

                    if len(current_positions) != len(previous_positions):
                        changes['keyword_changes'].append({
                            'keyword': keyword,
                            'old_count': len(previous_positions),
                            'new_count': len(current_positions)
                        })

        return changes if any(changes.values()) else None

    def send_telegram_notification(self, heylink_data, changes):
        """Telegram'a bildirim gönder"""
        try:
            message = f"🔄 **{heylink_data['name']}** - Değişiklik Algılandı!\n\n"
            message += f"📅 {datetime.now().strftime('%H:%M:%S')}\n"
            message += f"🔗 {heylink_data['url']}\n\n"

            if changes.get('new_links'):
                message += f"🆕 **Yeni Linkler ({len(changes['new_links'])}):**\n"
                for link in changes['new_links'][:5]:  # İlk 5 taneyi göster
                    message += f"• {link['text']}\n"
                if len(changes['new_links']) > 5:
                    message += f"... ve {len(changes['new_links']) - 5} tane daha\n"
                message += "\n"

            if changes.get('removed_links'):
                message += f"❌ **Silinen Linkler ({len(changes['removed_links'])}):**\n"
                for link in changes['removed_links'][:5]:
                    message += f"• {link['text']}\n"
                message += "\n"

            if changes.get('position_changes'):
                message += f"📊 **Pozisyon Değişiklikleri ({len(changes['position_changes'])}):**\n"
                for change in changes['position_changes'][:10]:
                    direction = "⬆️" if change['new_position'] < change['old_position'] else "⬇️"
                    message += f"{direction} {change['link']}: {change['old_position']} → {change['new_position']}\n"
                message += "\n"

            if changes.get('keyword_changes'):
                message += f"🎯 **Anahtar Kelime Değişiklikleri:**\n"
                for change in changes['keyword_changes']:
                    message += f"• '{change['keyword']}': {change['old_count']} → {change['new_count']}\n"
                message += "\n"

            # Tüm chat ID'lerine gönder
            for chat_id in self.chat_ids:
                try:
                    self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    self.logger.info(f"Bildirim gönderildi: {chat_id}")
                except TelegramError as e:
                    self.logger.error(f"Telegram hatası {chat_id}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Bildirim gönderme hatası: {str(e)}")

    def check_all_heylinks(self):
        """Tüm heylink'leri paralel olarak kontrol et"""
        print(f"\n🔍 {len(self.config['heylinks'])} sayfa kontrol ediliyor...")

        with ThreadPoolExecutor(max_workers=self.config['settings']['max_concurrent_requests']) as executor:
            # Tüm heylink'ler için future'lar oluştur
            futures = [executor.submit(self.scrape_heylink, heylink) for heylink in self.config['heylinks']]

            completed = 0
            changes_found = 0

            for future in as_completed(futures):
                try:
                    current_data = future.result()
                    completed += 1

                    if current_data['status'] == 'success':
                        # Önceki veriyi yükle
                        previous_data = self.load_previous_data(current_data['id'])

                        # Değişiklikleri kontrol et
                        changes = self.find_changes(current_data, previous_data)

                        if changes:
                            changes_found += 1
                            print(f"✨ Değişiklik: {current_data['name']}")

                            # Bildirim gönder
                            self.send_telegram_notification(current_data, changes)

                        # Yeni veriyi kaydet
                        self.save_data(current_data)

                    else:
                        print(f"❌ Hata: {current_data['name']} - {current_data['error']}")

                    # Progress göster
                    progress = (completed / len(self.config['heylinks'])) * 100
                    print(".1f", end='', flush=True)

                except Exception as e:
                    self.logger.error(f"İşlem hatası: {str(e)}")

            print(f"\n✅ Kontrol tamamlandı! {changes_found} değişiklik bulundu.")

    def run_continuous(self):
        """Sürekli çalışma modu"""
        print("🔄 Sürekli takip modu başlatıldı...")

        while True:
            try:
                self.check_all_heylinks()
                print(f"⏰ Sonraki kontrol: {self.config['telegram']['notification_interval']} saniye sonra")
                time.sleep(self.config['telegram']['notification_interval'])

            except KeyboardInterrupt:
                print("\n🛑 Sistem durduruldu.")
                break
            except Exception as e:
                self.logger.error(f"Sistem hatası: {str(e)}")
                time.sleep(60)  # Hata durumunda 1 dakika bekle

if __name__ == "__main__":
    tracker = HeylinkTracker()
    tracker.run_continuous()
