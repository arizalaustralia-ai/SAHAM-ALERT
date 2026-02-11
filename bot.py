import requests
from bs4 import BeautifulSoup
import os
import feedparser

# --- KONFIGURASI ---
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Sumber Data
URL_IDX = 'https://www.idx.co.id/en/listed-companies/corporate-actions/'
URL_CNBC = 'https://www.cnbcindonesia.com/investment/feed' 
URL_KONTAN = 'https://investasi.kontan.co.id/rss'
URL_INVESTOR = 'https://www.investor.id/rss/investasi'

def send_telegram_message(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Error: Secrets tidak ditemukan")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    requests.post(url, json=payload)

def check_idx():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(URL_IDX, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        if not table: return []
        
        rows = table.find_all('tr')[1:6] 
        keywords = ["akuisisi", "merger", "divestasi", "private placement", "right issue", "joint venture", "free float", "direktur", "direksi"]
        
        news = []
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 0:
                ticker = cols[1].text.strip()
                action = cols[2].text.strip()
                if any(key in action.lower() for key in keywords):
                    news.append(f"🏢 <b>IDX: {ticker}</b> - {action}")
        return news
    except Exception as e:
        print(f"Error IDX: {e}")
        return []

def check_rss(url, source_name):
    try:
        feed = feedparser.parse(url)
        news = []
        
        # --- KEMBALIKAN KE KEYWORD FOKUS ---
        business_keywords = ["merambah", "diversifikasi", "lini bisnis baru", "fokus baru", "bidang usaha baru", "backdoor", "ekspansi ke", "transformasi bisnis", "HMETD", "kepemilikan", "pengendali", "konglo", "laporan keuangan", "LK", "corporate action", "target price", "laba"]
        
        for entry in feed.entries[:2]: 
            title = entry.title
            link = entry.link
            
            # Cek apakah judul berita mengandung kata kunci perubahan bisnis
            if any(keyword in title.lower() for keyword in business_keywords):
                news.append(f"📰 <b>{source_name}:</b> {title}\n<a href='{link}'>Baca</a>")
        return news
    except Exception as e:
        print(f"Error RSS {source_name}: {e}")
        return []

if __name__ == "__main__":
    all_news = []
    all_news.extend(check_idx())
    all_news.extend(check_rss(URL_CNBC, "CNBC"))
    all_news.extend(check_rss(URL_KONTAN, "Kontan"))
    all_news.extend(check_rss(URL_INVESTOR, "Investor"))

    if all_news:
        message = "🚨 <b>Alert Saham & Ekspansi Bisnis:</b>\n\n" + "\n\n".join(all_news)
        send_telegram_message(message)
    else:
        print("Tidak ada berita yang sesuai kata kunci hari ini.")
