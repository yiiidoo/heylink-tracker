#!/bin/bash

echo "🚂 Railway Deployment"
echo "==================="

# Railway CLI kontrolü
if ! command -v railway &> /dev/null; then
    echo "📦 Railway CLI yükleniyor..."
    if curl -fsSL https://railway.app/install.sh | sh; then
        echo "✅ Railway CLI yüklendi"
    else
        echo "❌ Railway CLI yüklenemedi"
        exit 1
    fi
fi

# Railway login
echo "🔑 Railway'e giriş yapın..."
railway login

# Proje oluştur
echo "📁 Proje oluşturuluyor..."
railway init heylink-tracker

# Environment variables
echo "⚙️  Environment variables ayarlanıyor..."
railway variables set TELEGRAM_BOT_TOKEN=7795627429:AAHdzjkww7WEUSXRsgG38rHMre4bMFG4mpw
railway variables set TELEGRAM_CHAT_ID=7155382465

# Deploy
echo "🚀 Deploy ediliyor..."
railway deploy

echo "✅ Railway deployment tamamlandı!"
echo ""
echo "Railway dashboard'dan projenizi kontrol edin:"
echo "https://railway.app/dashboard"
