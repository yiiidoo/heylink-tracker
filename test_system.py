#!/usr/bin/env python3
"""
Heylink Tracker Sistem Testi
"""

import os
import json
import time
from heylink_tracker import HeylinkTracker

def test_config():
    """Config dosyasını test et"""
    print("🧪 Config testi...")

    if not os.path.exists('config.json'):
        print("❌ config.json bulunamadı!")
        return False

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        required_keys = ['telegram', 'heylinks', 'settings']
        for key in required_keys:
            if key not in config:
                print(f"❌ {key} anahtarı eksik!")
                return False

        if len(config['heylinks']) == 0:
            print("❌ Hiç heylink URL'i yok!")
            return False

        print("✅ Config dosyası geçerli.")
        return True

    except json.JSONDecodeError as e:
        print(f"❌ JSON parse hatası: {e}")
        return False

def test_imports():
    """Gerekli import'ları test et"""
    print("🧪 Import testi...")

    try:
        import requests
        import bs4
        import telegram
        import schedule
        print("✅ Tüm import'lar başarılı.")
        return True
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        return False

def test_telegram_bot():
    """Telegram bot bağlantısını test et"""
    print("🧪 Telegram bot testi...")

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        token = config['telegram']['bot_token']
        chat_ids = config['telegram']['chat_ids']

        if token == 'YOUR_BOT_TOKEN_HERE':
            print("⚠️  Bot token'ı ayarlanmamış!")
            return False

        import telegram
        bot = telegram.Bot(token=token)

        # Bot bilgilerini al
        bot_info = bot.get_me()
        print(f"✅ Bot bağlandı: @{bot_info.username}")

        # Chat ID'lerini test et
        for chat_id in chat_ids:
            if chat_id == 'YOUR_CHAT_ID_HERE':
                print("⚠️  Chat ID ayarlanmamış!")
                continue
            try:
                bot.send_message(chat_id=chat_id, text="🧪 Test mesajı")
                print(f"✅ {chat_id} chat ID'si çalışıyor.")
            except Exception as e:
                print(f"❌ {chat_id} chat ID'si hatalı: {e}")

        return True

    except Exception as e:
        print(f"❌ Telegram bot hatası: {e}")
        return False

def test_single_scrape():
    """Tek bir sayfayı scrape et"""
    print("🧪 Sayfa scrape testi...")

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)

        if not config['heylinks']:
            print("❌ Test edilecek sayfa yok!")
            return False

        # İlk sayfayı test et
        test_heylink = config['heylinks'][0]

        tracker = HeylinkTracker()
        result = tracker.scrape_heylink(test_heylink)

        if result['status'] == 'success':
            print(f"✅ {result['name']} başarıyla scrape edildi.")
            print(f"   Başlık: {result['title']}")
            print(f"   Link sayısı: {len(result['links'])}")
            return True
        else:
            print(f"❌ Scrape hatası: {result['error']}")
            return False

    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

def run_full_test():
    """Tam sistem testini çalıştır"""
    print("🚀 Heylink Tracker - Tam Sistem Testi")
    print("=" * 50)

    tests = [
        ("Config Kontrolü", test_config),
        ("Import Kontrolü", test_imports),
        ("Telegram Bot", test_telegram_bot),
        ("Sayfa Scrape", test_single_scrape)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
            print("✅ PASSED")
        else:
            print("❌ FAILED")

    print(f"\n📊 Test Sonuçları: {passed}/{total}")

    if passed == total:
        print("🎉 Tüm testler başarılı! Sistem hazır.")
        print("\nSistemi başlatmak için:")
        print("  python3 run.py start")
    else:
        print("⚠️  Bazı testler başarısız. Sorunları çözün.")

    return passed == total

if __name__ == "__main__":
    run_full_test()
