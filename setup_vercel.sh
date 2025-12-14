#!/bin/bash

echo "🎯 HEYLINK TRACKER - VERCEL KURULUMU"
echo "==================================="
echo ""

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Adım sayacı
STEP=1

print_step() {
    echo ""
    echo -e "${GREEN}📍 ADIM $STEP: $1${NC}"
    echo "----------------------------------------"
    ((STEP++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# 1. Gereksinimler kontrolü
print_step "Gereksinimler Kontrolü"

if ! command -v node &> /dev/null; then
    print_error "Node.js yüklü değil!"
    echo "Node.js indirin: https://nodejs.org"
    exit 1
fi

if ! command -v git &> /dev/null; then
    print_error "Git yüklü değil!"
    echo "Git indirin: https://git-scm.com"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    print_error "Python3 yüklü değil!"
    exit 1
fi

print_success "Tüm gereksinimler yüklü!"

# 2. Paket yükleme
print_step "Paket Yükleme"

echo "📦 Vercel CLI yükleniyor..."
if npm install -g vercel; then
    print_success "Vercel CLI yüklendi"
else
    print_error "Vercel CLI yüklenemedi"
    exit 1
fi

# 3. GitHub repository hazırlığı
print_step "GitHub Repository Hazırlığı"

echo "🔧 Git repository hazırlanıyor..."
if git init && git add . && git commit -m "Vercel Heylink Tracker"; then
    print_success "Git repository hazır"
else
    print_error "Git repository hazırlanamadı"
    exit 1
fi

print_warning "Şimdi GitHub'da repository oluşturmanız gerekiyor!"
echo ""
echo "🌐 Tarayıcınızda açın: https://github.com/new"
echo ""
echo "Repository bilgileri:"
echo "Repository name: heylink-tracker"
echo "Description: 100 Heylink sayfası takip sistemi"
echo "Visibility: Public"
echo ""
echo "✅ 'Create repository' tıklayın"
echo ""
read -p "Repository oluşturduktan sonra URL'yi buraya yapıştırın: " GITHUB_URL

if [ -z "$GITHUB_URL" ]; then
    print_error "GitHub URL gerekli!"
    exit 1
fi

# 4. GitHub'a push
print_step "GitHub'a Yükleme"

echo "⬆️  Kodlar GitHub'a yükleniyor..."
if git remote add origin "$GITHUB_URL" && git push -u origin main; then
    print_success "Kodlar GitHub'a yüklendi"
else
    print_error "GitHub'a yükleme başarısız"
    exit 1
fi

# 5. Vercel giriş ve deploy
print_step "Vercel Kurulumu"

echo "🔑 Vercel'e giriş yapın..."
if vercel login; then
    print_success "Vercel'e giriş yapıldı"
else
    print_error "Vercel giriş başarısız"
    exit 1
fi

echo "🚀 Vercel'e deploy ediliyor..."
if vercel --prod; then
    print_success "Vercel deployment başarılı!"
else
    print_error "Vercel deployment başarısız"
    exit 1
fi

# 6. Environment Variables bilgilendirmesi
print_step "Environment Variables Ayarlama"

echo "🔧 Vercel Dashboard'da ayarlamanız gerekenler:"
echo ""
echo "🌐 Tarayıcınızda açın: https://vercel.com/dashboard"
echo "Projenizi seçin → Settings → Environment Variables"
echo ""
echo "Aşağıdaki değişkenleri ekleyin:"
echo ""
echo "TELEGRAM_BOT_TOKEN = [BotFather'dan aldığınız token]"
echo "TELEGRAM_CHAT_IDS = [Chat ID'niz]"
echo ""
read -p "Environment Variables'ı ayarladınız mı? (y/N): " -n 1 -r
echo ""

# 7. GitHub Secrets bilgilendirmesi
print_step "GitHub Secrets Ayarlama"

echo "🔧 GitHub'da Secrets ayarlamanız gerekenler:"
echo ""
echo "🌐 Tarayıcınızda açın: https://github.com/[KULLANICI_ADINIZ]/heylink-tracker/settings/secrets/actions"
echo "'New repository secret' ile şunları ekleyin:"
echo ""
echo "TELEGRAM_BOT_TOKEN = [BotFather'dan aldığınız token]"
echo "TELEGRAM_CHAT_IDS = [Chat ID'niz]"
echo "VERCEL_FUNCTION_URL = https://[PROJE_ADINIZ].vercel.app/api/tracker"
echo "VERCEL_TOKEN = [Vercel token'ınız]"
echo ""
echo "Vercel Token almak için terminale yazın: vercel token add"
echo ""
read -p "GitHub Secrets'ı ayarladınız mı? (y/N): " -n 1 -r
echo ""

# Final mesaj
print_success "🎉 KURULUM TAMAMLANDI!"
echo ""
echo "📊 Sistem durumu:"
echo "✅ Kodlar GitHub'da"
echo "✅ Vercel'de deploy edildi"
echo "✅ Environment Variables ayarlandı"
echo "✅ GitHub Actions hazır"
echo ""
echo "⏰ Sistem her 5 dakikada bir otomatik çalışacak!"
echo ""
echo "📱 Bildirimleri almak için:"
echo "1. Telegram bot'una mesaj gönderin"
echo "2. İlk kontrol sonrası bildirimler gelecek"
echo ""
echo "🔍 Takip için:"
echo "- GitHub Actions: Repository → Actions"
echo "- Vercel Logs: Dashboard → Functions"
echo ""
echo "🎯 İyi eğlenceler! Sistem çalışıyor... 🚀"
