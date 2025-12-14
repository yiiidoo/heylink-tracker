#!/usr/bin/env python3
"""
Heylink URL Ekleme Scripti
Mevcut config'e yeni URL'ler ekler
"""

import json
import random

def load_config():
    """Config dosyasını yükle"""
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ config.json bulunamadı!")
        return None

def save_config(config):
    """Config dosyasını kaydet"""
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("✅ Config kaydedildi.")

def add_custom_urls():
    """Kullanıcıdan URL'ler alıp config'e ekle"""
    config = load_config()
    if not config:
        return

    print("🔗 Özel Heylink URL'leri ekleyin")
    print("Örnek: https://heylink.me/benim_sayfam")
    print("Boş satır girerek bitirin.")
    print()

    new_urls = []
    while True:
        url = input("URL girin (veya boş bırakın): ").strip()
        if not url:
            break

        if not url.startswith('https://heylink.me/'):
            print("❌ URL https://heylink.me/ ile başlamalı!")
            continue

        # URL'den isim çıkar
        name = url.replace('https://heylink.me/', '').replace('_', ' ').title()

        new_urls.append({
            'id': f"custom_{len(config['heylinks']) + len(new_urls) + 1}",
            'url': url,
            'name': name,
            'check_interval': 300 + random.randint(0, 60),
            'track_keywords': [name.lower().replace(' ', '')]
        })

        print(f"✅ {name} eklendi.")

    if new_urls:
        config['heylinks'].extend(new_urls)
        save_config(config)
        print(f"\n🎉 {len(new_urls)} yeni URL eklendi! Toplam: {len(config['heylinks'])}")
    else:
        print("❌ Hiç URL eklenmedi.")

def add_bulk_urls():
    """Toplu URL ekleme"""
    config = load_config()
    if not config:
        return

    print("📋 Toplu URL ekleme")
    print("Her satıra bir URL yazın:")
    print("https://heylink.me/url1")
    print("https://heylink.me/url2")
    print("...")
    print()

    urls_text = ""
    print("URL'leri girin (Ctrl+D ile bitirin):")
    try:
        while True:
            line = input()
            urls_text += line + "\n"
    except EOFError:
        pass

    urls = [line.strip() for line in urls_text.split('\n') if line.strip()]

    new_urls = []
    for url in urls:
        if url.startswith('https://heylink.me/'):
            name = url.replace('https://heylink.me/', '').replace('_', ' ').title()

            new_urls.append({
                'id': f"bulk_{len(config['heylinks']) + len(new_urls) + 1}",
                'url': url,
                'name': name,
                'check_interval': 300 + random.randint(0, 60),
                'track_keywords': [name.lower().replace(' ', '')]
            })

    if new_urls:
        config['heylinks'].extend(new_urls)
        save_config(config)
        print(f"\n🎉 {len(new_urls)} yeni URL eklendi! Toplam: {len(config['heylinks'])}")
    else:
        print("❌ Geçerli URL bulunamadı.")

def list_urls():
    """Mevcut URL'leri listele"""
    config = load_config()
    if not config:
        return

    print(f"📋 Mevcut URL'ler ({len(config['heylinks'])}):")
    print("-" * 50)

    for i, heylink in enumerate(config['heylinks'], 1):
        print(f"{i:3d}. {heylink['name']}")
        print(f"     {heylink['url']}")
        print(f"     ID: {heylink['id']}")
        print()

def remove_url():
    """URL sil"""
    list_urls()

    config = load_config()
    if not config:
        return

    try:
        index = int(input("Silinecek URL'nin numarası: ")) - 1
        if 0 <= index < len(config['heylinks']):
            removed = config['heylinks'].pop(index)
            save_config(config)
            print(f"✅ {removed['name']} silindi.")
        else:
            print("❌ Geçersiz numara!")
    except ValueError:
        print("❌ Geçersiz giriş!")

def main():
    print("🔗 Heylink URL Yönetimi")
    print("=" * 30)

    while True:
        print()
        print("1. Özel URL ekle")
        print("2. Toplu URL ekle")
        print("3. URL'leri listele")
        print("4. URL sil")
        print("5. Çıkış")
        print()

        choice = input("Seçiminiz: ").strip()

        if choice == '1':
            add_custom_urls()
        elif choice == '2':
            add_bulk_urls()
        elif choice == '3':
            list_urls()
        elif choice == '4':
            remove_url()
        elif choice == '5':
            break
        else:
            print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    main()
