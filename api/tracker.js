import axios from 'axios';
import * as cheerio from 'cheerio';
import TelegramBot from 'node-telegram-bot-api';
import crypto from 'crypto';

// Global değişkenler (Vercel'de persist etmez ama basit için OK)
let previousData = {};

async function checkHeylinks() {
  const results = {
    pagesChecked: 0,
    changesFound: 0,
    errors: 0
  };

  for (const heylink of CONFIG.heylinks) {
    try {
      results.pagesChecked++;

      // Sayfa scrape et
      const currentData = await scrapeHeylink(heylink);

      if (currentData.status === 'success') {
        // Önceki veri ile karşılaştır
        const prevData = previousData[heylink.id];
        const changes = findChanges(currentData, prevData);

        if (changes) {
          results.changesFound++;
        }

        // Yeni veriyi kaydet
        previousData[heylink.id] = currentData;
      } else {
        results.errors++;
      }

    } catch (error) {
      console.error(`Hata ${heylink.name}:`, error.message);
      results.errors++;
    }
  }

  return results;
}

async function scrapeHeylink(heylink) {
  try {
    const response = await axios.get(heylink.url, {
      timeout: CONFIG.settings.request_timeout,
      headers: {
        'User-Agent': CONFIG.settings.user_agent
      }
    });

    const $ = cheerio.load(response.data);

    // Sayfa başlığını al
    const title = $('title').text() || "Başlık bulunamadı";

    // Tüm linkleri topla
    const links = [];
    $('a[href]').each((i, element) => {
      const linkText = $(element).text().trim();
      if (linkText && linkText.length > 2) {
        links.push({
          text: linkText,
          href: $(element).attr('href'),
          position: links.length + 1
        });
      }
    });

    // Sayfa hash'i oluştur
    const pageContent = links.map(link => link.href + link.text).join('');
    const hash = crypto.createHash('md5').update(pageContent).digest('hex');

    return {
      id: heylink.id,
      url: heylink.url,
      name: heylink.name,
      title: title,
      links: links,
      hash: hash,
      timestamp: new Date().toISOString(),
      status: 'success'
    };

  } catch (error) {
    return {
      id: heylink.id,
      url: heylink.url,
      name: heylink.name,
      status: 'error',
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

function findChanges(currentData, previousData) {
  if (!previousData || previousData.status === 'error') {
    return null;
  }

  const changes = {
    new_links: [],
    removed_links: [],
    position_changes: []
  };

  // Hash karşılaştırması
  if (currentData.hash !== previousData.hash) {
    changes.hash_changed = true;

    // Link karşılaştırması
    const currentLinks = new Map(currentData.links.map(link => [link.href, link]));
    const previousLinks = new Map(previousData.links.map(link => [link.href, link]));

    // Yeni linkler
    for (const [href, link] of currentLinks) {
      if (!previousLinks.has(href)) {
        changes.new_links.push(link);
      }
    }

    // Silinen linkler
    for (const [href, link] of previousLinks) {
      if (!currentLinks.has(href)) {
        changes.removed_links.push(link);
      }
    }

    // Pozisyon değişiklikleri
    for (const [href, currentLink] of currentLinks) {
      if (previousLinks.has(href)) {
        const prevLink = previousLinks.get(href);
        if (Math.abs(currentLink.position - prevLink.position) >= 3) {
          changes.position_changes.push({
            link: currentLink.text,
            old_position: prevLink.position,
            new_position: currentLink.position
          });
        }
      }
    }
  }

  return Object.keys(changes).some(key => Array.isArray(changes[key]) ? changes[key].length > 0 : changes[key]) ? changes : null;
}

async function sendTelegramUpdate(results) {
  try {
    const bot = new TelegramBot(CONFIG.telegram.bot_token);

    let message = `🤖 **Heylink Tracker - Kontrol Tamamlandı**\n\n`;
    message += `📅 ${new Date().toLocaleString('tr-TR')}\n`;
    message += `📊 ${results.pagesChecked} sayfa kontrol edildi\n`;
    message += `🔄 ${results.changesFound} değişiklik bulundu\n`;

    if (results.errors > 0) {
      message += `⚠️ ${results.errors} hata oluştu\n`;
    }

    message += `\n🔄 Her 5 dakikada bir kontrol ediliyor`;

    // Tüm chat ID'lerine gönder
    for (const chatId of CONFIG.telegram.chat_ids) {
      try {
        await bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
      } catch (error) {
        console.error(`Telegram gönderim hatası ${chatId}:`, error.message);
      }
    }

  } catch (error) {
    console.error('Telegram güncelleme hatası:', error.message);
  }
}

const CONFIG = {
  telegram: {
    bot_token: process.env.TELEGRAM_BOT_TOKEN || '',
    chat_ids: [],
    notification_interval: 300
  },
  heylinks: [
    {
      id: "sorunsuz",
      url: "https://heylink.me/sorunsuz",
      name: "Sorunsuz Ana Sayfa",
      check_interval: 300,
      track_keywords: ["volacasinonun"]
    }
  ],
  settings: {
    max_concurrent_requests: 5,
    request_timeout: 20000,
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  }
};

async function scrapeHeylink(heylink) {
  try {
    const response = await axios.get(heylink.url, {
      timeout: CONFIG.settings.request_timeout,
      headers: {
        'User-Agent': CONFIG.settings.user_agent
      }
    });

    const $ = cheerio.load(response.data);

    // Sayfa başlığını al
    const title = $('title').text() || "Başlık bulunamadı";

    // Tüm linkleri topla
    const links = [];
    $('a[href]').each((i, element) => {
      const linkText = $(element).text().trim();
      if (linkText && linkText.length > 2) {
        links.push({
          text: linkText,
          href: $(element).attr('href'),
          position: links.length + 1
        });
      }
    });

    // Sayfa hash'i oluştur
    const pageContent = links.map(link => link.href + link.text).join('');
    const hash = crypto.createHash('md5').update(pageContent).digest('hex');

    return {
      id: heylink.id,
      url: heylink.url,
      name: heylink.name,
      title: title,
      links: links,
      hash: hash,
      timestamp: new Date().toISOString(),
      status: 'success'
    };

  } catch (error) {
    return {
      id: heylink.id,
      url: heylink.url,
      name: heylink.name,
      status: 'error',
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

function findChanges(currentData, previousData) {
  if (!previousData || previousData.status === 'error') {
    return null;
  }

  const changes = {
    new_links: [],
    removed_links: [],
    position_changes: []
  };

  // Hash karşılaştırması
  if (currentData.hash !== previousData.hash) {
    changes.hash_changed = true;

    // Link karşılaştırması
    const currentLinks = new Map(currentData.links.map(link => [link.href, link]));
    const previousLinks = new Map(previousData.links.map(link => [link.href, link]));

    // Yeni linkler
    for (const [href, link] of currentLinks) {
      if (!previousLinks.has(href)) {
        changes.new_links.push(link);
      }
    }

    // Silinen linkler
    for (const [href, link] of previousLinks) {
      if (!currentLinks.has(href)) {
        changes.removed_links.push(link);
      }
    }

    // Pozisyon değişiklikleri
    for (const [href, currentLink] of currentLinks) {
      if (previousLinks.has(href)) {
        const prevLink = previousLinks.get(href);
        if (Math.abs(currentLink.position - prevLink.position) >= 3) {
          changes.position_changes.push({
            link: currentLink.text,
            old_position: prevLink.position,
            new_position: currentLink.position
          });
        }
      }
    }
  }

  return Object.keys(changes).some(key => Array.isArray(changes[key]) ? changes[key].length > 0 : changes[key]) ? changes : null;
}

async function sendTelegramNotification(heylinkData, changes) {
  try {
    if (!CONFIG.telegram.bot_token || !CONFIG.telegram.chat_ids.length) {
      console.log('Telegram config eksik');
      return;
    }

    const bot = new TelegramBot(CONFIG.telegram.bot_token);

    let message = `🔄 **${heylinkData.name}** - Değişiklik Algılandı!\n\n`;
    message += `📅 ${new Date().toLocaleString('tr-TR')}\n`;
    message += `🔗 ${heylinkData.url}\n\n`;

    if (changes.new_links?.length) {
      message += `🆕 **Yeni Linkler (${changes.new_links.length}):**\n`;
      changes.new_links.slice(0, 3).forEach(link => {
        message += `• ${link.text}\n`;
      });
      message += '\n';
    }

    if (changes.removed_links?.length) {
      message += `❌ **Silinen Linkler (${changes.removed_links.length}):**\n`;
      changes.removed_links.slice(0, 3).forEach(link => {
        message += `• ${link.text}\n`;
      });
      message += '\n';
    }

    if (changes.position_changes?.length) {
      message += `📊 **Önemli Pozisyon Değişiklikleri (${changes.position_changes.length}):**\n`;
      changes.position_changes.slice(0, 5).forEach(change => {
        const direction = change.new_position < change.old_position ? '⬆️' : '⬇️';
        message += `${direction} ${change.link}: ${change.old_position} → ${change.new_position}\n`;
      });
      message += '\n';
    }

    // Tüm chat ID'lerine gönder
    for (const chatId of CONFIG.telegram.chat_ids) {
      if (chatId.trim()) {
        try {
          await bot.sendMessage(chatId.trim(), message, { parse_mode: 'Markdown' });
          console.log(`Bildirim gönderildi: ${chatId}`);
        } catch (error) {
          console.error(`Telegram hatası ${chatId}:`, error.message);
        }
      }
    }

  } catch (error) {
    console.error('Bildirim gönderme hatası:', error.message);
  }
}

async function sendStatusNotification(message) {
  try {
    if (!CONFIG.telegram.bot_token || !CONFIG.telegram.chat_ids.length) {
      console.log('Telegram config eksik');
      return;
    }

    const bot = new TelegramBot(CONFIG.telegram.bot_token);

    const statusMessage = `🤖 **Heylink Tracker - Sistem Durumu**\n\n`;
    statusMessage += `📅 ${new Date().toLocaleString('tr-TR')}\n`;
    statusMessage += `💻 ${message}\n\n`;
    statusMessage += `🔄 Her 5 dakikada bir kontrol ediliyor`;

    for (const chatId of CONFIG.telegram.chat_ids) {
      if (chatId.trim()) {
        try {
          await bot.sendMessage(chatId.trim(), statusMessage, { parse_mode: 'Markdown' });
          console.log(`Durum bildirimi gönderildi: ${chatId}`);
        } catch (error) {
          console.error(`Telegram hatası ${chatId}:`, error.message);
        }
      }
    }

  } catch (error) {
    console.error('Durum bildirimi hatası:', error.message);
  }
}

async function checkAllHeylinks() {
  console.log(`🔍 ${CONFIG.heylinks.length} sayfa kontrol ediliyor...`);

  // Sistem aktif bildirimi gönder
  await sendStatusNotification(`🔍 ${CONFIG.heylinks.length} sayfa kontrol ediliyor...`);

  let changesFound = 0;
  let errors = 0;

  for (const heylink of CONFIG.heylinks) {
    try {
      console.log(`Kontrol ediliyor: ${heylink.name}`);

      // Mevcut veriyi çek
      const currentData = await scrapeHeylink(heylink);

      if (currentData.status === 'success') {
        // Önceki veriyi al
        const previousDataItem = previousData[heylink.id];

        // Değişiklikleri kontrol et
        const changes = findChanges(currentData, previousDataItem);

        if (changes) {
          changesFound++;
          console.log(`✨ Değişiklik: ${heylink.name}`);

          // Bildirim gönder
          await sendTelegramNotification(currentData, changes);
        }

        // Yeni veriyi sakla
        previousData[heylink.id] = currentData;

      } else {
        console.log(`❌ Hata: ${heylink.name} - ${currentData.error}`);
        errors++;
      }

    } catch (error) {
      console.error(`İşlem hatası ${heylink.name}:`, error.message);
      errors++;
    }
  }

  // Final durum bildirimi
  const finalMessage = `✅ Kontrol tamamlandı!\n📊 ${CONFIG.heylinks.length} sayfa kontrol edildi\n🔄 ${changesFound} değişiklik bulundu`;
  if (errors > 0) {
    finalMessage += `\n⚠️ ${errors} hata oluştu`;
  }

  await sendStatusNotification(finalMessage);

  console.log(`✅ Kontrol tamamlandı! ${changesFound} değişiklik, ${errors} hata.`);
  return changesFound;
}

export default async function handler(request, response) {
  // Method kontrolü
  if (request.method !== 'POST') {
    return response.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Environment variables kontrolü
    const botToken = process.env.TELEGRAM_BOT_TOKEN;
    const chatIds = process.env.TELEGRAM_CHAT_IDS;

    if (!botToken) {
      return response.status(200).json({
        status: 'error',
        message: 'TELEGRAM_BOT_TOKEN not set',
        timestamp: new Date().toISOString()
      });
    }

    if (!chatIds) {
      return response.status(200).json({
        status: 'error',
        message: 'TELEGRAM_CHAT_IDS not set',
        timestamp: new Date().toISOString()
      });
    }

    // Sadece basit response döndür
    return response.status(200).json({
      status: 'success',
      message: 'Function çalışıyor - scraping devre dışı',
      timestamp: new Date().toISOString(),
      env_check: {
        bot_token: !!CONFIG.telegram.bot_token,
        chat_ids_count: CONFIG.telegram.chat_ids.length
      }
    });

  } catch (error) {
    console.error('Handler hatası:', error.message);
    return response.status(500).json({
      status: 'error',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
}