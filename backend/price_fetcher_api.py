"""
KaratMate Labs - Live Gold Price Fetcher API
Provides CORS-enabled endpoints for browser-based price fetching
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Default email configuration (hardcoded for easy use)
DEFAULT_EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'fasin.absons@gmail.com',
    'app_password': 'zrxj vfjt wjos wkwy',
    'recipient_email': 'faseen1532@gmail.com'
}

# Customs duty rates for red channel (males)
# Source: Indian Customs regulations
CUSTOMS_RED_CHANNEL_RATES = {
    # Weight in grams: (rate_percentage, description)
    'up_to_20g': (0.06, '6% for up to 20 grams'),
    'above_20g': (0.125, '12.5% for above 20 grams (males)')
}


def extract_price(text):
    """Extract numeric price from text"""
    # Remove currency symbols and commas
    text = text.replace(',', '').replace('₹', '').replace('AED', '').replace('/10gm', '').replace('/gm', '').replace('/', '').strip()
    # Find number
    match = re.search(r'(\d+\.?\d*)', text)
    if match:
        return float(match.group(1))
    return None


def calculate_sovereign_uae(price_per_gram, grams=8):
    """
    Calculate sovereign price for UAE
    Formula: (price_per_gram * grams) + 8% making charges + 5% VAT
    Note: 8% is average, can be higher
    """
    base_price = price_per_gram * grams
    making_charges = base_price * 0.08  # 8% (average)
    subtotal = base_price + making_charges
    vat = base_price * 0.05  # 5%
    total = subtotal + vat
    
    return {
        'base_price': round(base_price, 2),
        'making_charges': round(making_charges, 2),
        'subtotal': round(subtotal, 2),
        'vat': round(vat, 2),
        'total': round(total, 2),
        'grams': grams
    }


def calculate_sovereign_india(price_per_10gm, grams=8):
    """
    Calculate sovereign price for India
    Formula: (price/10 * grams) + 12% making + 3% GST on making + 5% GST on total
    """
    price_per_gram = price_per_10gm / 10
    base_price = price_per_gram * grams
    
    making_charges = base_price * 0.12  # 12% making charges (minimum)
    making_gst = making_charges * 0.03  # 3% GST on making
    subtotal = base_price + making_charges + making_gst
    gst = base_price * 0.05  # 5% GST on total
    total = subtotal + gst
    
    return {
        'base_price': round(base_price, 2),
        'making_charges': round(making_charges, 2),
        'making_gst': round(making_gst, 2),
        'subtotal': round(subtotal, 2),
        'gst': round(gst, 2),
        'total': round(total, 2),
        'grams': grams
    }


def calculate_customs_duty(base_price_inr, grams, channel='red'):
    """
    Calculate customs duty when bringing gold from UAE to India
    
    Args:
        base_price_inr: Base gold value in INR (without making/GST)
        grams: Weight in grams
        channel: 'red' (6%) or 'green' (33%)
    
    Rules:
    - Red Channel: 6%
    - Green Channel: 33%
    - ₹50,000 exemption
    """
    exemption = 50000
    
    if base_price_inr <= exemption:
        return {
            'gold_value': base_price_inr,
            'exemption': exemption,
            'taxable_amount': 0,
            'customs_duty': 0,
            'gst_on_duty': 0,
            'total_with_gst': 0,
            'total_without_gst': 0,
            'channel': channel.upper(),
            'grams': grams,
            'duty_rate': '0%'
        }
    
    taxable_amount = base_price_inr - exemption
    
    # Calculate duty based on channel
    if channel.lower() == 'red':
        customs_rate = 0.06  # 6% for red channel
        rate_display = '6%'
    else:
        customs_rate = 0.33  # 33% for green channel
        rate_display = '33%'
    
    customs_duty = taxable_amount * customs_rate
    
    # Round up to nearest 50
    import math
    customs_duty_rounded = math.ceil(customs_duty / 50) * 50
    
    # GST is optional (5% of customs duty)
    gst_on_duty = customs_duty_rounded * 0.05
    gst_rounded = math.ceil(gst_on_duty / 50) * 50
    
    return {
        'gold_value': round(base_price_inr, 2),
        'exemption': exemption,
        'taxable_amount': round(taxable_amount, 2),
        'customs_duty': customs_duty_rounded,
        'gst_on_duty': gst_rounded,
        'total_with_gst': customs_duty_rounded + gst_rounded,
        'total_without_gst': customs_duty_rounded,
        'channel': channel.upper(),
        'duty_rate': rate_display,
        'grams': grams
    }


@app.route('/api/fetch/sourcea', methods=['GET'])
def fetch_sourcea():
    """Fetch Source A (UAE) prices via server (bypasses CORS) - Multiple selectors for robustness"""
    print("\n📊 [KaratMate Labs] Fetching Source A (UAE) prices...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get('https://eshop.joyalukkas.com/', headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            prices = {}
            
            # Multiple selector strategies for robustness
            selectors = [
                '#myModal table',  # Primary selector
                '.gold-rate-attribute-list table',  # Alternate class
                'div.modal-body table',  # Modal body table
                'table tbody'  # Generic table
            ]
            
            modal = None
            for selector in selectors:
                modal = soup.select_one(selector)
                if modal:
                    print(f"   ✅ Found table using selector: {selector}")
                    break
            
            if modal:
                rows = modal.find_all('tr')
                for idx, row in enumerate(rows):
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        karat = cells[0].text.strip().lower()
                        price_text = cells[1].text.strip()
                        price = extract_price(price_text)
                        
                        if price and karat:
                            prices[karat] = price
                        
                        print(f"   Row {idx+1}: {karat} = {price_text} -> {price}")
            
            # Try CSS selectors as backup
            if not prices:
                css_selectors = [
                    ('#myModal > div > div > div > div.modal-body > div > table > tbody > tr:nth-child(1) > td:nth-child(2)', '24k'),
                    ('#myModal > div > div > div > div.modal-body > div > table > tbody > tr:nth-child(2) > td:nth-child(2)', '22k'),
                    ('#myModal > div > div > div > div.modal-body > div > table > tbody > tr:nth-child(3) > td:nth-child(2)', '18k')
                ]
                
                for selector, karat in css_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        price = extract_price(elem.text)
                        if price:
                            prices[karat] = price
            
            if prices:
                result = {
                    'success': True,
                    'source': 'Source A (UAE)',
                    'timestamp': datetime.now().isoformat(),
                    'prices': prices,
                    'currency': 'AED',
                    'location': 'UAE',
                    'provider': 'KaratMate Labs'
                }
                print(f"   ✅ [KaratMate Labs] Source A (UAE): {prices}")
                return jsonify(result)
        
        return jsonify({
            'success': False,
            'error': 'Could not fetch prices',
            'provider': 'KaratMate Labs'
        }), 500
    
    except Exception as e:
        print(f"   ❌ [KaratMate Labs] Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'provider': 'KaratMate Labs'
        }), 500


@app.route('/api/fetch/sourceb', methods=['GET'])
def fetch_sourceb():
    """Fetch Source B prices via server (bypasses CORS) - Multiple selectors for robustness"""
    print("\n📊 [KaratMate Labs] Fetching Source B prices...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get('https://www.candere.com/gold-rate-today/kerala', 
                               headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            prices = {}
            
            # Multiple selectors for 24K
            selectors_24k = [
                '.goldCard--one .goldCard--rate',  # Primary
                '.goldCard.goldCard--one .goldCard--left p.goldCard--rate',  # Full path
                '#maincontent > div.columns > div > div.goldRateWrapper > div.sectionBanner > div > div > div.goldCard__wrapper > div.goldCard.goldCard--one > div',  # CSS selector
                'div.goldCard--one p'  # Generic
            ]
            
            for selector in selectors_24k:
                card_24k = soup.select_one(selector)
                if card_24k:
                    price_text = card_24k.text.strip()
                    price = extract_price(price_text)
                    if price:
                        prices['24k'] = price
                        print(f"   ✅ 24K found using: {selector} = {price}")
                        break
            
            # Multiple selectors for 22K
            selectors_22k = [
                '.goldCard--two .goldCard--rate',  # Primary
                '.goldCard.goldCard--two .goldCard--left p.goldCard--rate',  # Full path
                '#maincontent > div.columns > div > div.goldRateWrapper > div.sectionBanner > div > div > div.goldCard__wrapper > div.goldCard.goldCard--two',  # CSS selector
                'div.goldCard--two p'  # Generic
            ]
            
            for selector in selectors_22k:
                card_22k = soup.select_one(selector)
                if card_22k:
                    price_text = card_22k.text.strip()
                    price = extract_price(price_text)
                    if price:
                        prices['22k'] = price
                        print(f"   ✅ 22K found using: {selector} = {price}")
                        break
            
            if prices:
                result = {
                    'success': True,
                    'source': 'Source B',
                    'timestamp': datetime.now().isoformat(),
                    'prices': prices,
                    'currency': 'INR',
                    'location': 'Kerala, India',
                    'unit': '10gm',
                    'provider': 'KaratMate Labs'
                }
                print(f"   ✅ [KaratMate Labs] Source B: {prices}")
                return jsonify(result)
        
        return jsonify({
            'success': False,
            'error': 'Could not fetch prices',
            'provider': 'KaratMate Labs'
        }), 500
    
    except Exception as e:
        print(f"   ❌ [KaratMate Labs] Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'provider': 'KaratMate Labs'
        }), 500


@app.route('/api/fetch/bhima', methods=['GET'])
def fetch_bhima():
    """Fetch Bhima Jewellers prices (UAE) - Multiple selectors for robustness"""
    print("\n📊 [KaratMate Labs] Fetching Bhima prices...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get('https://bhima.ae/gold-rates/', headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            prices = {}
            
            # Try multiple strategies to find prices
            # Strategy 1: Look for price tables
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        karat_text = cells[0].text.strip().lower()
                        price_text = cells[1].text.strip()
                        
                        if '24' in karat_text:
                            price = extract_price(price_text)
                            if price and price > 200:  # Sanity check
                                prices['24k'] = price
                        elif '22' in karat_text:
                            price = extract_price(price_text)
                            if price and price > 200:
                                prices['22k'] = price
                        elif '18' in karat_text:
                            price = extract_price(price_text)
                            if price and price > 150:
                                prices['18k'] = price
            
            # Strategy 2: Look for divs with price classes
            if not prices:
                price_divs = soup.find_all(['div', 'span', 'p'], class_=lambda x: x and ('price' in x.lower() or 'rate' in x.lower()))
                for div in price_divs:
                    text = div.text.strip()
                    if '24' in text:
                        price = extract_price(text)
                        if price:
                            prices['24k'] = price
                    elif '22' in text:
                        price = extract_price(text)
                        if price:
                            prices['22k'] = price
            
            if prices:
                result = {
                    'success': True,
                    'source': 'Bhima Jewellers',
                    'timestamp': datetime.now().isoformat(),
                    'prices': prices,
                    'currency': 'AED',
                    'location': 'UAE',
                    'provider': 'KaratMate Labs'
                }
                print(f"   ✅ [KaratMate Labs] Bhima: {prices}")
                return jsonify(result)
        
        return jsonify({
            'success': False,
            'error': 'Could not fetch prices',
            'provider': 'KaratMate Labs'
        }), 500
    
    except Exception as e:
        print(f"   ❌ [KaratMate Labs] Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'provider': 'KaratMate Labs'
        }), 500


@app.route('/api/fetch/all', methods=['GET'])
def fetch_all():
    """Fetch prices from all sources"""
    print("\n📊 [KaratMate Labs] Fetching all prices...")
    return jsonify(fetch_all_internal())


def send_email_report(data):
    """Send email with gold price report and calculations"""
    print("\n📧 Sending email report...")
    
    try:
        # Use default config
        config = DEFAULT_EMAIL_CONFIG
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🏅 KaratMate Labs - Gold Price Report {datetime.now().strftime('%d %b %Y, %I:%M %p')}"
        msg['From'] = config['sender_email']
        msg['To'] = config['recipient_email']
        
        # Create HTML email
        html = generate_email_html(data)
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['sender_email'], config['app_password'])
            server.send_message(msg)
        
        print(f"   ✅ Email sent to {config['recipient_email']}")
        return True
    
    except Exception as e:
        print(f"   ❌ Error sending email: {e}")
        return False


def generate_email_html(data):
    """Generate beautiful HTML email with all prices and calculations"""
    
    html = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
            }}
            .content {{
                padding: 30px;
            }}
            .section {{
                margin-bottom: 30px;
            }}
            .section h2 {{
                color: #667eea;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #667eea;
                color: white;
                font-weight: bold;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .highlight {{
                background-color: #fef3c7;
                font-weight: bold;
            }}
            .live-badge {{
                background: #ef4444;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
            }}
            .footer {{
                background: #f5f5f5;
                padding: 20px;
                text-align: center;
                color: #666;
                font-size: 14px;
            }}
            .price-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin: 20px 0;
            }}
            .price-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
            }}
            .price-card h3 {{
                margin: 0 0 15px 0;
                font-size: 16px;
            }}
            .price-item {{
                display: flex;
                justify-content: space-between;
                margin: 8px 0;
            }}
            .note {{
                background: #fef3c7;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #f59e0b;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏅 KaratMate Labs</h1>
                <p>Gold Price Report - <span class="live-badge">🔴 LIVE DATA</span></p>
                <p>{datetime.now().strftime('%A, %d %B %Y - %I:%M %p')}</p>
            </div>
            
            <div class="content">
    """
    
    # Live Prices Section
    if 'sources' in data:
        html += '<div class="section"><h2>📊 Current Live Prices</h2>'
        
        # Source A (UAE)
        if 'sourcea' in data['sources']:
            ja = data['sources']['sourcea']
            html += f"""
            <h3>KaratMate UAE (Source A (UAE))</h3>
            <table>
                <tr><th>Karat</th><th>Price (AED/gram)</th></tr>
                <tr><td>24K</td><td>{ja['prices'].get('24k', 'N/A')} AED</td></tr>
                <tr><td>22K</td><td>{ja['prices'].get('22k', 'N/A')} AED</td></tr>
                <tr><td>18K</td><td>{ja['prices'].get('18k', 'N/A')} AED</td></tr>
            </table>
            """
        
        # Source B
        if 'sourceb' in data['sources']:
            ca = data['sources']['sourceb']
            html += f"""
            <h3>KaratMate India (Source B (Kerala))</h3>
            <table>
                <tr><th>Karat</th><th>Price (INR/10gm)</th></tr>
                <tr><td>24K</td><td>₹{ca['prices'].get('24k', 'N/A')}/10gm</td></tr>
                <tr><td>22K</td><td>₹{ca['prices'].get('22k', 'N/A')}/10gm</td></tr>
            </table>
            """
        
        html += '</div>'
    
    # Sovereign Calculations
    if 'calculations' in data:
        calc = data['calculations']
        
        # UAE Calculations
        html += '<div class="section"><h2>💰 Sovereign Pricing (22K Gold)</h2>'
        
        if 'sourcea_8g' in calc:
            j8 = calc['sourcea_8g']
            html += f"""
            <h3>KaratMate UAE (8 grams - 1 Sovereign)</h3>
            <div class="note">
                <strong>Note:</strong> Making charges: 8% (average, can be higher) | VAT: 5%
            </div>
            <table>
                <tr><th>Description</th><th>Amount</th></tr>
                <tr><td>Base Price ({j8['grams']}g × price/gram)</td><td>AED {j8['base_price']}</td></tr>
                <tr><td>Making Charges (8%)</td><td>AED {j8['making_charges']}</td></tr>
                <tr><td>VAT (5%)</td><td>AED {j8['vat']}</td></tr>
                <tr class="highlight"><td><strong>Total Price</strong></td><td><strong>AED {j8['total']}</strong></td></tr>
            </table>
            """
        
        if 'sourcea_16g' in calc:
            j16 = calc['sourcea_16g']
            html += f"""
            <h3>KaratMate UAE (16 grams - 2 Sovereigns)</h3>
            <table>
                <tr><th>Description</th><th>Amount</th></tr>
                <tr><td>Base Price ({j16['grams']}g × price/gram)</td><td>AED {j16['base_price']}</td></tr>
                <tr><td>Making Charges (8%)</td><td>AED {j16['making_charges']}</td></tr>
                <tr><td>VAT (5%)</td><td>AED {j16['vat']}</td></tr>
                <tr class="highlight"><td><strong>Total Price</strong></td><td><strong>AED {j16['total']}</strong></td></tr>
            </table>
            """
        
        if 'sourcea_20g' in calc:
            j20 = calc['sourcea_20g']
            html += f"""
            <h3>KaratMate UAE (20 grams)</h3>
            <table>
                <tr><th>Description</th><th>Amount</th></tr>
                <tr><td>Base Price ({j20['grams']}g × price/gram)</td><td>AED {j20['base_price']}</td></tr>
                <tr><td>Making Charges (8%)</td><td>AED {j20['making_charges']}</td></tr>
                <tr><td>VAT (5%)</td><td>AED {j20['vat']}</td></tr>
                <tr class="highlight"><td><strong>Total Price</strong></td><td><strong>AED {j20['total']}</strong></td></tr>
            </table>
            """
        
        if 'sourceb_8g' in calc:
            c8 = calc['sourceb_8g']
            html += f"""
            <h3>KaratMate India (8 grams - 1 Sovereign)</h3>
            <div class="note">
                <strong>Note:</strong> Making charges: 12% (minimum) | Making GST: 3% | GST: 5%
            </div>
            <table>
                <tr><th>Description</th><th>Amount</th></tr>
                <tr><td>Base Price ({c8['grams']}g × price/gram)</td><td>₹{c8['base_price']}</td></tr>
                <tr><td>Making Charges (12%)</td><td>₹{c8['making_charges']}</td></tr>
                <tr><td>Making GST (3%)</td><td>₹{c8['making_gst']}</td></tr>
                <tr><td>GST (5%)</td><td>₹{c8['gst']}</td></tr>
                <tr class="highlight"><td><strong>Total Price</strong></td><td><strong>₹{c8['total']}</strong></td></tr>
            </table>
            """
        
        if 'sourceb_16g' in calc:
            c16 = calc['sourceb_16g']
            html += f"""
            <h3>KaratMate India (16 grams - 2 Sovereigns)</h3>
            <table>
                <tr><th>Description</th><th>Amount</th></tr>
                <tr><td>Base Price ({c16['grams']}g × price/gram)</td><td>₹{c16['base_price']}</td></tr>
                <tr><td>Making Charges (12%)</td><td>₹{c16['making_charges']}</td></tr>
                <tr><td>Making GST (3%)</td><td>₹{c16['making_gst']}</td></tr>
                <tr><td>GST (5%)</td><td>₹{c16['gst']}</td></tr>
                <tr class="highlight"><td><strong>Total Price</strong></td><td><strong>₹{c16['total']}</strong></td></tr>
            </table>
            """
        
        if 'sourceb_20g' in calc:
            c20 = calc['sourceb_20g']
            html += f"""
            <h3>KaratMate India (20 grams)</h3>
            <table>
                <tr><th>Description</th><th>Amount</th></tr>
                <tr><td>Base Price ({c20['grams']}g × price/gram)</td><td>₹{c20['base_price']}</td></tr>
                <tr><td>Making Charges (12%)</td><td>₹{c20['making_charges']}</td></tr>
                <tr><td>Making GST (3%)</td><td>₹{c20['making_gst']}</td></tr>
                <tr><td>GST (5%)</td><td>₹{c20['gst']}</td></tr>
                <tr class="highlight"><td><strong>Total Price</strong></td><td><strong>₹{c20['total']}</strong></td></tr>
            </table>
            """
        
        html += '</div>'
        
        # Customs Calculations
        html += '<div class="section"><h2>🛃 Customs Duty Calculator</h2>'
        html += '<p>When bringing gold from UAE to India (Base gold value only, without making charges)</p>'
        html += '<div class="note"><strong>Note:</strong> ₹50,000 exemption applied | Red Channel: 6% | Green Channel: 33% | Rounded to nearest ₹50</div>'
        
        if 'customs_8g_red' in calc:
            cr8 = calc['customs_8g_red']
            cg8 = calc.get('customs_8g_green', {})
            
            html += f"""
            <h3>For 8 grams (1 Sovereign)</h3>
            <table>
                <tr><th>Channel</th><th>Gold Value</th><th>Exemption</th><th>Taxable</th><th>Duty Rate</th><th>Customs Duty</th><th>With GST (5%)*</th></tr>
                <tr>
                    <td><strong>RED Channel</strong></td>
                    <td>₹{cr8['gold_value']}</td>
                    <td>-₹{cr8['exemption']}</td>
                    <td>₹{cr8['taxable_amount']}</td>
                    <td>{cr8['duty_rate']}</td>
                    <td class="highlight">₹{cr8['customs_duty']}</td>
                    <td>₹{cr8['total_with_gst']}</td>
                </tr>
            """
            
            if cg8:
                html += f"""
                <tr>
                    <td><strong>GREEN Channel</strong></td>
                    <td>₹{cg8['gold_value']}</td>
                    <td>-₹{cg8['exemption']}</td>
                    <td>₹{cg8['taxable_amount']}</td>
                    <td>{cg8['duty_rate']}</td>
                    <td class="highlight">₹{cg8['customs_duty']}</td>
                    <td>₹{cg8['total_with_gst']}</td>
                </tr>
                """
            
            html += '</table>'
        
        if 'customs_16g_red' in calc:
            cr16 = calc['customs_16g_red']
            cg16 = calc.get('customs_16g_green', {})
            
            html += f"""
            <h3>For 16 grams (2 Sovereigns)</h3>
            <table>
                <tr><th>Channel</th><th>Gold Value</th><th>Exemption</th><th>Taxable</th><th>Duty Rate</th><th>Customs Duty</th><th>With GST (5%)*</th></tr>
                <tr>
                    <td><strong>RED Channel</strong></td>
                    <td>₹{cr16['gold_value']}</td>
                    <td>-₹{cr16['exemption']}</td>
                    <td>₹{cr16['taxable_amount']}</td>
                    <td>{cr16['duty_rate']}</td>
                    <td class="highlight">₹{cr16['customs_duty']}</td>
                    <td>₹{cr16['total_with_gst']}</td>
                </tr>
            """
            
            if cg16:
                html += f"""
                <tr>
                    <td><strong>GREEN Channel</strong></td>
                    <td>₹{cg16['gold_value']}</td>
                    <td>-₹{cg16['exemption']}</td>
                    <td>₹{cg16['taxable_amount']}</td>
                    <td>{cg16['duty_rate']}</td>
                    <td class="highlight">₹{cg16['customs_duty']}</td>
                    <td>₹{cg16['total_with_gst']}</td>
                </tr>
                """
            
            html += '</table>'
        
        if 'customs_20g_red' in calc:
            cr20 = calc['customs_20g_red']
            cg20 = calc.get('customs_20g_green', {})
            
            html += f"""
            <h3>For 20 grams</h3>
            <table>
                <tr><th>Channel</th><th>Gold Value</th><th>Exemption</th><th>Taxable</th><th>Duty Rate</th><th>Customs Duty</th><th>With GST (5%)*</th></tr>
                <tr>
                    <td><strong>RED Channel</strong></td>
                    <td>₹{cr20['gold_value']}</td>
                    <td>-₹{cr20['exemption']}</td>
                    <td>₹{cr20['taxable_amount']}</td>
                    <td>{cr20['duty_rate']}</td>
                    <td class="highlight">₹{cr20['customs_duty']}</td>
                    <td>₹{cr20['total_with_gst']}</td>
                </tr>
            """
            
            if cg20:
                html += f"""
                <tr>
                    <td><strong>GREEN Channel</strong></td>
                    <td>₹{cg20['gold_value']}</td>
                    <td>-₹{cg20['exemption']}</td>
                    <td>₹{cg20['taxable_amount']}</td>
                    <td>{cg20['duty_rate']}</td>
                    <td class="highlight">₹{cg20['customs_duty']}</td>
                    <td>₹{cg20['total_with_gst']}</td>
                </tr>
                """
            
            html += '</table>'
        
        html += '<p><small>* GST on customs duty is optional and depends on customs officer</small></p>'
        html += '</div>'
    
    html += """
            </div>
            
            <div class="footer">
                <p><strong>🏅 Powered by KaratMate Labs</strong></p>
                <p>This report contains live gold prices and calculations.</p>
                <p>Making charges: UAE 8% (average, can be higher), India 12% (minimum)</p>
                <p>Customs: Red Channel 6%, Green Channel 33% | ₹50,000 exemption</p>
                <p><small>Generated automatically - Do not reply to this email</small></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


@app.route('/api/fetch-and-email', methods=['POST'])
def fetch_and_email():
    """Fetch prices and send email report"""
    print("\n" + "="*60)
    print("  🏅 KaratMate Labs - Fetch & Email Report")
    print("="*60)
    
    # Fetch all prices and calculations
    data = fetch_all_internal()
    
    if data['success']:
        # Send email
        email_sent = send_email_report(data)
        
        return jsonify({
            'success': True,
            'email_sent': email_sent,
            'data': data,
            'provider': 'KaratMate Labs'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch prices',
            'provider': 'KaratMate Labs'
        }), 500


def fetch_all_internal():
    """Internal function to fetch all prices (used by both /api/fetch/all and email)"""
    results = {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'sources': {},
        'provider': 'KaratMate Labs'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Fetch Source A (UAE)
    try:
        response = requests.get('https://eshop.joyalukkas.com/', headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            modal = soup.select_one('#myModal table')
            
            prices = {}
            if modal:
                rows = modal.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        karat = cells[0].text.strip().lower()
                        price_text = cells[1].text.strip()
                        price = extract_price(price_text)
                        if price and karat:
                            prices[karat] = price
            
            if prices:
                results['sources']['sourcea'] = {
                    'prices': prices,
                    'currency': 'AED',
                    'location': 'UAE'
                }
                print(f"   ✅ [KaratMate Labs] Source A (UAE): 24K={prices.get('24k')} AED, 22K={prices.get('22k')} AED")
    except Exception as e:
        print(f"   ❌ [KaratMate Labs] Source A (UAE) Error: {e}")
    
    # Fetch Source B
    try:
        response = requests.get('https://www.candere.com/gold-rate-today/kerala', 
                               headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            prices = {}
            card_24k = soup.select_one('.goldCard--one .goldCard--rate')
            if card_24k:
                price = extract_price(card_24k.text.strip())
                if price:
                    prices['24k'] = price
            
            card_22k = soup.select_one('.goldCard--two .goldCard--rate')
            if card_22k:
                price = extract_price(card_22k.text.strip())
                if price:
                    prices['22k'] = price
            
            if prices:
                results['sources']['sourceb'] = {
                    'prices': prices,
                    'currency': 'INR',
                    'location': 'Kerala, India',
                    'unit': '10gm'
                }
                print(f"   ✅ [KaratMate Labs] Source B: 24K=₹{prices.get('24k')}/10gm, 22K=₹{prices.get('22k')}/10gm")
    except Exception as e:
        print(f"   ❌ [KaratMate Labs] Source B Error: {e}")
    
    # Add calculations
    results['calculations'] = {}
    
    # Calculate UAE sovereign prices (8g, 16g, and 20g)
    if 'sourcea' in results['sources']:
        price_22k = results['sources']['sourcea']['prices'].get('22k')
        if price_22k:
            results['calculations']['sourcea_8g'] = calculate_sovereign_uae(price_22k, 8)
            results['calculations']['sourcea_16g'] = calculate_sovereign_uae(price_22k, 16)
            results['calculations']['sourcea_20g'] = calculate_sovereign_uae(price_22k, 20)
    
    # Calculate India sovereign prices and customs (8g, 16g, and 20g)
    if 'sourceb' in results['sources']:
        price_22k = results['sources']['sourceb']['prices'].get('22k')
        if price_22k:
            # Sovereign calculations
            results['calculations']['sourceb_8g'] = calculate_sovereign_india(price_22k, 8)
            results['calculations']['sourceb_16g'] = calculate_sovereign_india(price_22k, 16)
            results['calculations']['sourceb_20g'] = calculate_sovereign_india(price_22k, 20)
            
            # Customs calculations (base price only, no making/GST)
            price_per_gram = price_22k / 10
            base_8g = price_per_gram * 8
            base_16g = price_per_gram * 16
            base_20g = price_per_gram * 20
            
            results['calculations']['customs_8g_red'] = calculate_customs_duty(base_8g, 8, 'red')
            results['calculations']['customs_8g_green'] = calculate_customs_duty(base_8g, 8, 'green')
            results['calculations']['customs_16g_red'] = calculate_customs_duty(base_16g, 16, 'red')
            results['calculations']['customs_16g_green'] = calculate_customs_duty(base_16g, 16, 'green')
            results['calculations']['customs_20g_red'] = calculate_customs_duty(base_20g, 20, 'red')
            results['calculations']['customs_20g_green'] = calculate_customs_duty(base_20g, 20, 'green')
    
    return results


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'provider': 'KaratMate Labs',
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🏅 KaratMate Labs - Live Gold Price API")
    print("="*60)
    print("  API Server running at: http://localhost:5002")
    print("  Endpoints:")
    print("    GET  /api/health")
    print("    GET  /api/fetch/sourcea")
    print("    GET  /api/fetch/sourceb")
    print("    GET  /api/fetch/bhima")
    print("    GET  /api/fetch/all")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5002)

