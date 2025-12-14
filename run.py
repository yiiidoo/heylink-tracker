#!/usr/bin/env python3
"""
Heylink Tracker Çalıştırma Scripti
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def check_requirements():
    """Gerekli paketlerin kurulu olup olmadığını kontrol et"""
    try:
        import requests
        import bs4
        import telegram
        print("✅ Tüm gerekli paketler kurulu.")
        return True
    except ImportError as e:
        print(f"❌ Eksik paket: {e}")
        print("📦 Paketleri yüklemek için: pip install -r requirements.txt")
        return False

def install_requirements():
    """Gerekli paketleri yükle"""
    print("📦 Paketler yükleniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Paketler başarıyla yüklendi.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Paket yükleme hatası: {e}")
        return False

def check_config():
    """Config dosyasını kontrol et"""
    if not os.path.exists('config.json'):
        print("❌ config.json dosyası bulunamadı!")
        return False

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Telegram token kontrolü
        if config['telegram']['bot_token'] == 'YOUR_BOT_TOKEN_HERE':
            print("⚠️  Telegram bot token'ı ayarlanmamış!")
            print("   BotFather'dan token alın ve config.json'a ekleyin.")
            return False

        # Chat ID kontrolü
        if 'YOUR_CHAT_ID_HERE' in config['telegram']['chat_ids']:
            print("⚠️  Telegram chat ID'si ayarlanmamış!")
            print("   Bot'a mesaj gönderin ve chat ID'yi öğrenin.")
            return False

        print("✅ Config dosyası hazır.")
        return True

    except Exception as e:
        print(f"❌ Config dosyası hatası: {e}")
        return False

def get_chat_id(token):
    """Bot'un chat ID'sini öğren"""
    try:
        import telegram
        bot = telegram.Bot(token=token)
        updates = bot.get_updates()
        if updates:
            chat_id = updates[-1].message.chat_id
            print(f"📱 Chat ID'niz: {chat_id}")
            return chat_id
        else:
            print("⚠️  Bot'a henüz mesaj gönderilmemiş.")
            print("   Telegram'da bot'a '/start' yazın ve tekrar deneyin.")
            return None
    except Exception as e:
        print(f"❌ Chat ID alınamadı: {e}")
        return None

def run_once():
    """Sistemi bir kez çalıştır (test için)"""
    print("🔍 Tek seferlik kontrol başlatılıyor...")
    try:
        # Config yükle
        with open('config.json', 'r') as f:
            config = json.load(f)

        # Sadece ilk 5 heylink'i test et
        test_heylinks = config['heylinks'][:5]

        # Test için geçici config oluştur
        test_config = config.copy()
        test_config['heylinks'] = test_heylinks

        # Geçici config dosyası oluştur
        with open('test_config.json', 'w') as f:
            json.dump(test_config, f, indent=2)

        # Test çalıştır
        result = subprocess.run([sys.executable, 'heylink_tracker.py'],
                              env={**os.environ, 'CONFIG_PATH': 'test_config.json'},
                              capture_output=True, text=True, timeout=300)

        # Geçici dosyayı sil
        os.remove('test_config.json')

        if result.returncode == 0:
            print("✅ Test tamamlandı!")
            print(result.stdout)
        else:
            print("❌ Test hatası:")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print("⏰ Test zaman aşımına uğradı (5 dakika)")
    except Exception as e:
        print(f"❌ Test hatası: {e}")

def run_continuous():
    """Sistemi sürekli çalıştır"""
    print("🔄 Sürekli takip modu başlatılıyor...")
    print("Durdurmak için Ctrl+C'ye basın.")
    try:
        subprocess.run([sys.executable, 'heylink_tracker.py'])
    except KeyboardInterrupt:
        print("\n🛑 Sistem durduruldu.")
    except Exception as e:
        print(f"❌ Çalıştırma hatası: {e}")

def main():
    print("🚀 Heylink Tracker Kontrol Paneli")
    print("=" * 40)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        print("Komutlar:")
        print("  setup    - Sistem kurulum ve kontrol")
        print("  install  - Paketleri yükle")
        print("  config   - Config kontrolü")
        print("  chatid   - Chat ID öğren")
        print("  test     - Tek seferlik test çalıştır")
        print("  start    - Sürekli takip başlat")
        print()
        command = input("Komut girin: ").strip().lower()

    if command == 'setup':
        print("🔧 Sistem kurulumu başlatılıyor...")

        if not check_requirements():
            if install_requirements():
                check_requirements()
            else:
                return

        check_config()

    elif command == 'install':
        install_requirements()

    elif command == 'config':
        check_config()

    elif command == 'chatid':
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)

            token = config['telegram']['bot_token']
            if token != 'YOUR_BOT_TOKEN_HERE':
                chat_id = get_chat_id(token)
                if chat_id:
                    print(f"Bu chat ID'yi config.json'daki 'chat_ids' listesine ekleyin:")
                    print(f'  "{chat_id}"')
            else:
                print("❌ Önce bot token'ını ayarlayın!")

        except Exception as e:
            print(f"❌ Hata: {e}")

    elif command == 'test':
        if check_requirements() and check_config():
            run_once()
        else:
            print("❌ Önce setup'ı çalıştırın!")

    elif command == 'start':
        if check_requirements() and check_config():
            run_continuous()
        else:
            print("❌ Önce setup'ı çalıştırın!")

    else:
        print("❌ Geçersiz komut!")

if __name__ == "__main__":
    main()
