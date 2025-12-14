#!/bin/bash

echo "🔑 GitHub Personal Access Token Ayarlama"
echo "========================================="

echo "🌐 GitHub'da Personal Access Token oluşturun:"
echo ""
echo "1. Tarayıcınızda açın: https://github.com/settings/tokens"
echo "2. 'Generate new token (classic)' tıklayın"
echo "3. Note: 'Heylink Tracker'"
echo "4. Expiration: 'No expiration'"
echo "5. Scopes: Sadece 'repo' işaretleyin"
echo "6. 'Generate token' tıklayın"
echo "7. Token'ı kopyalayın (şu format: ghp_...)"
echo ""

read -p "Token'ı buraya yapıştırın: " GITHUB_TOKEN

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ Token gerekli!"
    exit 1
fi

# Git config
git config --global user.name "yiiidooo"
git config --global user.email "yigitmatador@gmail.com"

# Remote URL'yi token ile güncelle
GITHUB_URL="https://oauth2:$GITHUB_TOKEN@github.com/yiiidoo/heylink-tracker.git"

echo "🔧 Git remote ayarlanıyor..."
git remote remove origin 2>/dev/null || true
git remote add origin "$GITHUB_URL"

echo "⬆️  Kodlar yükleniyor..."
if git push -u origin main; then
    echo "✅ Başarıyla yüklendi!"
    echo ""
    echo "🎉 GitHub kısmı tamamlandı!"
    echo "Şimdi Vercel kısmına geçebilirsiniz."
else
    echo "❌ Yükleme başarısız!"
    echo "Token'ı kontrol edin ve tekrar deneyin."
fi
