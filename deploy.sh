#!/bin/bash

echo "🚀 Heylink Tracker Vercel Deployment"
echo "=================================="

# Vercel CLI kontrolü
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI yüklü değil. Yüklemek için:"
    echo "npm install -g vercel"
    exit 1
fi

# Vercel giriş kontrolü
if ! vercel whoami &> /dev/null; then
    echo "🔑 Vercel'e giriş yapmanız gerekiyor:"
    vercel login
fi

echo "📦 Projeyi Vercel'e deploy ediyorum..."

# Production deployment
vercel --prod

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment başarılı!"
    echo ""
    echo "📋 Sonraki adımlar:"
    echo "1. Vercel dashboard'dan Environment Variables ekleyin"
    echo "2. GitHub repository oluşturun"
    echo "3. GitHub Secrets ekleyin"
    echo "4. GitHub Actions otomatik çalışacaktır!"
    echo ""
    echo "🔗 Vercel URL'inizi alın ve VERCEL_FUNCTION_URL olarak kaydedin"
else
    echo ""
    echo "❌ Deployment başarısız!"
    echo "Hata için yukarıdaki mesajları kontrol edin."
fi
