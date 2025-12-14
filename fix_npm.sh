#!/bin/bash

echo "🔧 NPM Permission Fix"
echo "===================="

# npm config fix
echo "📦 npm config ayarlanıyor..."
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'

# PATH'e ekleme
echo "export PATH=~/.npm-global/bin:\$PATH" >> ~/.zshrc
echo "export PATH=~/.npm-global/bin:\$PATH" >> ~/.bashrc

# PATH'i güncelle
export PATH=~/.npm-global/bin:$PATH

echo "✅ npm permission problemi çözüldü!"
echo ""
echo "Şimdi tekrar deneyin:"
echo "cd /Users/yiiidooo/Downloads/heylink"
echo "./setup_vercel.sh"
