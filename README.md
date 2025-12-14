# 🚀 Heylink Tracker - 100 Sayfa Takip Sistemi

Bu sistem 100 farklı heylink.me sayfasını aynı anda takip eder ve sıralama değişikliklerini Telegram botu ile bildirir.

## ☁️ Vercel Deployment (0 Maliyet - Local Kaynak Yok)

Bu proje Vercel + GitHub Actions ile **tamamen ücretsiz** ve **7/24** çalışır!

## 📋 Özellikler

- ✅ **100 Sayfa** aynı anda takip
- ✅ **Paralel İşleme** (10 eş zamanlı istek)
- ✅ **Telegram Bildirimleri** (anlık)
- ✅ **Değişiklik Takibi** (pozisyon, yeni/silinen linkler)
- ✅ **Anahtar Kelime Takibi** (belirli linkleri öncelikli takip)
- ✅ **JSON Veri Saklama** (geçmiş veriler)
- ✅ **Hata Yönetimi** (bağlantı kopmaları, timeout'lar)
- ✅ **Loglama** (detaylı kayıtlar)

## 🛠️ Kurulum

### 1. Gereksinimler
```bash
python3 --version  # 3.7+ gerekli
```

### 2. Paketleri Yükle
```bash
pip install -r requirements.txt
```

### 3. Telegram Bot Oluştur
1. [@BotFather](https://t.me/botfather)'a gidin
2. `/newbot` yazın
3. Bot ismi ve username belirleyin
4. Token'ı alın

### 4. Config Dosyasını Düzenle
`config.json` dosyasını açın ve düzenleyin:

```json
{
  "telegram": {
    "bot_token": "BOT_TOKEN_BURAYA",
    "chat_ids": ["CHAT_ID_BURAYA"],
    "notification_interval": 300
  }
}
```

### 5. Chat ID'yi Öğrenin
```bash
python3 run.py chatid
```
(Bot'a mesaj gönderdikten sonra çalıştırın)

## 🚀 Vercel + GitHub Actions Kurulumu (0 Maliyet)

### 1. Vercel Hesabı Oluşturun
- [vercel.com](https://vercel.com)'a gidin
- GitHub ile giriş yapın
- Ücretsiz planı seçin

### 2. GitHub Repository Oluşturun
```bash
# Bu projeyi GitHub'a yükleyin
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/KULLANICI_ADINIZ/heylink-tracker.git
git push -u origin main
```

### 3. Vercel'e Deploy Edin
```bash
# Otomatik deploy scripti
chmod +x deploy.sh
./deploy.sh

# Veya manuel:
# Vercel CLI yükleyin
npm install -g vercel

# Vercel'e giriş yapın
vercel login

# Projeyi deploy edin
vercel --prod

# Function URL'ini alın (örn: https://heylink-tracker.vercel.app/api/tracker)
```

### 4. Environment Variables Ayarlayın
Vercel dashboard'da **Settings > Environment Variables**:

```
TELEGRAM_BOT_TOKEN = your_bot_token_here
TELEGRAM_CHAT_IDS = your_chat_id_here
```

### 5. GitHub Secrets Ekleyin
Repository **Settings > Secrets and variables > Actions**:

```
TELEGRAM_BOT_TOKEN = your_bot_token_here
TELEGRAM_CHAT_IDS = your_chat_id_here
VERCEL_FUNCTION_URL = https://your-project.vercel.app/api/tracker
VERCEL_TOKEN = your_vercel_token_here
```

### 6. Sistemi Başlatın
GitHub Actions otomatik olarak her 5 dakikada bir çalışacaktır!

## 🖥️ Local Kullanım (Alternatif)

### Sistem Kurulumu
```bash
python3 run.py setup
```

### Test Çalıştır (5 sayfa)
```bash
python3 run.py test
```

### Sürekli Takip Başlat
```bash
python3 run.py start
```

## 📁 Dosya Yapısı

```
heylink/
├── config.json          # Ayarlar
├── heylink_tracker.py   # Ana takip scripti
├── run.py              # Çalıştırma scripti
├── requirements.txt     # Python paketleri
├── data/               # Sayfa verileri (JSON)
├── logs/               # Log dosyaları
└── README.md           # Bu dosya
```

## ⚙️ Yapılandırma

### Heylink URL'leri Düzenleme
`config.json`'daki `heylinks` bölümünü düzenleyin:

```json
{
  "id": "sayfa_id",
  "url": "https://heylink.me/sayfa_adi",
  "name": "Görünen İsim",
  "check_interval": 300,
  "track_keywords": ["volacasinonun", "diger_link"]
}
```

### Özel URL'ler Eklemek
`heylink_url_generator.py` scripti ile yeni URL'ler ekleyin:

```python
# Özel URL'lerinizi buraya ekleyin
custom_urls = [
    "https://heylink.me/benim_sayfam1",
    "https://heylink.me/benim_sayfam2",
    # ...
]
```

## 📊 Bildirim Türleri

Sistem şu değişiklikleri bildirir:

### 🔄 Pozisyon Değişiklikleri
- Linklerin sıralamadaki yer değişikliği
- 📈 Yükseliş/📉 Düşüş göstergeleri

### 🆕 Yeni Linkler
- Sayfaya yeni eklenen linkler
- İlk 5 tanesi detaylı gösterilir

### ❌ Silinen Linkler
- Sayfadan çıkarılan linkler

### 🎯 Anahtar Kelime Değişiklikleri
- Belirlediğiniz özel linklerin durumu

## 🔧 Gelişmiş Ayarlar

### Paralel İşlem Sayısı
```json
"max_concurrent_requests": 10
```
(Eş zamanlı istek sayısı - çok yüksek yapmayın!)

### Kontrol Aralığı
```json
"notification_interval": 300
```
(Saniye cinsinden - 5 dakika)

### Timeout Süresi
```json
"request_timeout": 30
```
(Sayfa yükleme timeout'u)

## 🐛 Sorun Giderme

### Bot Çalışmıyor
1. Token'ı kontrol edin
2. Chat ID'yi doğru ayarladınız mı?
3. Bot'a `/start` yazdınız mı?

### Sayfa Yüklenmiyor
1. URL'leri kontrol edin
2. İnternet bağlantınızı kontrol edin
3. User-Agent ayarlarını kontrol edin

### Çok Yavaş
1. `max_concurrent_requests` değerini azaltın
2. `check_interval` değerini artırın

## 📈 Performans

- **100 Sayfa**: ~30-60 saniye (paralel işleme bağlı)
- **Bellek Kullanımı**: ~50-100MB
- **CPU Kullanımı**: %10-30 (kontrol sırasında)
- **Disk Kullanımı**: ~10-50MB (veri + log'lar)

## 🔒 Güvenlik

- Bot token'ını kimseyle paylaşmayın
- Config dosyasını .gitignore'a ekleyin
- Hassas verileri log'lamayın

## 📞 Destek

Sorularınız için:
1. Log dosyalarını kontrol edin (`logs/` klasörü)
2. Test modunda çalıştırın (`python3 run.py test`)
3. Hata mesajlarını paylaşın

---

**Not**: Bu sistem heylink.me'nin kullanım şartlarına uygun şekilde kullanılmalıdır. Aşırı istek göndermeyin!
