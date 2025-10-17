"""
Gold Price Tracker - Automated Multi-Source Price Fetcher
Fetches gold prices from Kalyan Jewellers, Joy Alukkas, Bhima, and Candere
Calculates custom duties and sends email notifications
"""

import os
import sys
import json
import time
import smtplib
import requests
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import math


class GoldPriceTracker:
    """Track gold prices from multiple sources"""
    
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.prices = {}
        self.timestamp = datetime.now()
        
        # FIXED Gmail configuration for notifications
        self.gmail_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'fasin.absons@gmail.com',
            'sender_password': 'zrxj vfjt wjos wkwy',
            'recipient': 'faseen1532@gmail.com'
        }
        
        # API-based gold price fallback
        self.api_sources = {
            'goldapi': 'https://www.goldapi.io/api/XAU/USD',
            'metalpriceapi': 'https://api.metalpriceapi.com/v1/latest',
            'currencyapi': 'https://api.currencyapi.com/v3/latest'
        }
    
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            'sources': {
                'kalyan': True,
                'joy_alukkas': True,
                'bhima': True,
                'candere': True,
                'goldapi': True
            },
            'email': {
                'sender': 'fasin.absons@gmail.com',
                'password': 'zrxj vfjt wjos wkwy',
                'recipient': 'faseen1532@gmail.com'
            },
            'calculations': {
                'making_charges': 12,
                'making_gst': 3,
                'vat_gst': 5,
                'customs_exemption': 50000,
                'red_channel_rate': 6,
                'green_channel_rate': 33
            }
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Save default config
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
    
    def setup_driver(self, headless=True):
        """Setup Selenium Chrome driver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        return webdriver.Chrome(options=chrome_options)
    
    def fetch_kalyan_prices(self):
        """Fetch prices from Kalyan Jewellers"""
        print("\n📊 Fetching Kalyan Jewellers prices...")
        
        try:
            driver = self.setup_driver()
            driver.get("https://www.kalyanjewellers.net/gold-rate/Gold-Rate-Today")
            time.sleep(3)
            
            # Wait for price block
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "priceBlock"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            price_block = soup.find('div', class_='priceBlock')
            
            prices = {}
            if price_block:
                for modal in price_block.find_all('div', class_='modalClass'):
                    label = modal.find('label')
                    if label:
                        text = label.text
                        if '24' in text:
                            price_text = modal.text
                            price = self.extract_price(price_text)
                            if price:
                                prices['24k'] = price
                        elif '22' in text:
                            price_text = modal.text
                            price = self.extract_price(price_text)
                            if price:
                                prices['22k'] = price
                        elif '18' in text:
                            price_text = modal.text
                            price = self.extract_price(price_text)
                            if price:
                                prices['18k'] = price
            
            driver.quit()
            
            if prices:
                print(f"   ✅ Kalyan: 24K={prices.get('24k', 0)} AED, 22K={prices.get('22k', 0)} AED")
                self.prices['kalyan'] = {
                    'prices': prices,
                    'currency': 'AED',
                    'location': 'UAE'
                }
                return prices
            else:
                print("   ❌ No prices found")
                return None
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def fetch_joy_alukkas_prices(self):
        """Fetch prices from Joy Alukkas"""
        print("\n📊 Fetching Joy Alukkas prices...")
        
        try:
            driver = self.setup_driver()
            driver.get("https://eshop.joyalukkas.com/")
            time.sleep(3)
            
            # Find and click gold rate modal
            try:
                # Wait for modal to appear
                modal = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "myModal"))
                )
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                table = soup.select_one('#myModal table')
                
                prices = {}
                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            karat = cells[0].text.strip()
                            price_text = cells[1].text.strip()
                            price = self.extract_price(price_text)
                            if price and karat:
                                prices[karat.lower()] = price
                
                driver.quit()
                
                if prices:
                    print(f"   ✅ Joy Alukkas: 24K={prices.get('24k', 0)} AED, 22K={prices.get('22k', 0)} AED")
                    self.prices['joy_alukkas'] = {
                        'prices': prices,
                        'currency': 'AED',
                        'location': 'UAE'
                    }
                    return prices
                else:
                    print("   ❌ No prices found")
                    return None
            
            except Exception as e:
                print(f"   ❌ Error parsing modal: {e}")
                driver.quit()
                return None
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def fetch_bhima_prices(self):
        """Fetch prices from Bhima Jewellers"""
        print("\n📊 Fetching Bhima Jewellers prices...")
        
        try:
            driver = self.setup_driver()
            driver.get("https://bhima.ae/gold-rates/")
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find gold rate table
            prices = {}
            # Look for price elements (adjust selectors based on actual page structure)
            price_elements = soup.find_all(['div', 'span', 'td'], class_=lambda x: x and 'price' in x.lower())
            
            # Parse prices (adjust based on actual HTML structure)
            for elem in price_elements:
                text = elem.text.strip()
                if '24' in text:
                    price = self.extract_price(text)
                    if price:
                        prices['24k'] = price
                elif '22' in text:
                    price = self.extract_price(text)
                    if price:
                        prices['22k'] = price
            
            driver.quit()
            
            if prices:
                print(f"   ✅ Bhima: 24K={prices.get('24k', 0)} AED, 22K={prices.get('22k', 0)} AED")
                self.prices['bhima'] = {
                    'prices': prices,
                    'currency': 'AED',
                    'location': 'UAE'
                }
                return prices
            else:
                print("   ❌ No prices found")
                return None
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def fetch_candere_prices(self):
        """Fetch prices from Candere (India)"""
        print("\n📊 Fetching Candere prices (India)...")
        
        try:
            driver = self.setup_driver()
            driver.get("https://www.candere.com/gold-rate-today/kerala")
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            prices = {}
            
            # Find 24K price
            card_24k = soup.select_one('.goldCard--one .goldCard--rate')
            if card_24k:
                price_text = card_24k.text.strip()
                price = self.extract_price(price_text)
                if price:
                    prices['24k'] = price
            
            # Find 22K price
            card_22k = soup.select_one('.goldCard--two .goldCard--rate')
            if card_22k:
                price_text = card_22k.text.strip()
                price = self.extract_price(price_text)
                if price:
                    prices['22k'] = price
            
            driver.quit()
            
            if prices:
                print(f"   ✅ Candere: 24K=₹{prices.get('24k', 0)}/10gm, 22K=₹{prices.get('22k', 0)}/10gm")
                self.prices['candere'] = {
                    'prices': prices,
                    'currency': 'INR',
                    'location': 'Kerala, India',
                    'unit': '10gm'
                }
                return prices
            else:
                print("   ❌ No prices found")
                return None
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def extract_price(self, text):
        """Extract numeric price from text"""
        import re
        # Remove currency symbols and commas
        text = text.replace(',', '').replace('₹', '').replace('AED', '').replace('/10gm', '').replace('/gm', '')
        # Find number
        match = re.search(r'(\d+\.?\d*)', text)
        if match:
            return float(match.group(1))
        return None
    
    def fetch_goldapi_prices(self):
        """Fetch live gold prices from GoldAPI.io (free tier: 100 requests/month)"""
        print("\n📊 Fetching GoldAPI.io prices (International)...")
        
        try:
            # Using free Gold Price API
            response = requests.get('https://api.gold-api.com/price/XAU', timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Gold price in USD per troy ounce
                if 'price' in data:
                    usd_per_troy_oz = data['price']
                    
                    # Convert to AED per gram
                    # 1 troy oz = 31.1035 grams
                    # 1 USD ≈ 3.67 AED (approximate)
                    usd_to_aed = 3.67
                    gram_per_troy_oz = 31.1035
                    
                    # Calculate 24K price per gram in AED
                    aed_per_gram_24k = (usd_per_troy_oz / gram_per_troy_oz) * usd_to_aed
                    
                    # Calculate 22K and 18K based on purity
                    aed_per_gram_22k = aed_per_gram_24k * (22/24)
                    aed_per_gram_18k = aed_per_gram_24k * (18/24)
                    
                    prices = {
                        '24k': round(aed_per_gram_24k, 2),
                        '22k': round(aed_per_gram_22k, 2),
                        '18k': round(aed_per_gram_18k, 2)
                    }
                    
                    print(f"   ✅ GoldAPI: 24K={prices['24k']} AED, 22K={prices['22k']} AED")
                    self.prices['goldapi'] = {
                        'prices': prices,
                        'currency': 'AED',
                        'location': 'International (Live Market)',
                        'source': 'Gold-API.com'
                    }
                    return prices
            
            # Fallback to another free API
            print("   Trying alternative API...")
            response = requests.get('https://www.goldapi.io/api/XAU/USD', 
                                   headers={'x-access-token': 'goldapi-demo'}, 
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'price' in data:
                    usd_per_troy_oz = data['price']
                    usd_to_aed = 3.67
                    gram_per_troy_oz = 31.1035
                    
                    aed_per_gram_24k = (usd_per_troy_oz / gram_per_troy_oz) * usd_to_aed
                    aed_per_gram_22k = aed_per_gram_24k * (22/24)
                    aed_per_gram_18k = aed_per_gram_24k * (18/24)
                    
                    prices = {
                        '24k': round(aed_per_gram_24k, 2),
                        '22k': round(aed_per_gram_22k, 2),
                        '18k': round(aed_per_gram_18k, 2)
                    }
                    
                    print(f"   ✅ GoldAPI: 24K={prices['24k']} AED, 22K={prices['22k']} AED")
                    self.prices['goldapi'] = {
                        'prices': prices,
                        'currency': 'AED',
                        'location': 'International (Live Market)',
                        'source': 'GoldAPI.io'
                    }
                    return prices
            
            print("   ❌ No prices available from APIs")
            return None
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def calculate_sovereign_price_uae(self, price_per_gram):
        """
        Calculate 1 sovereign (8 grams) price for UAE
        Formula: (price_per_gram * 8) + 12% making charges + 5% VAT
        """
        base_price = price_per_gram * 8
        making_charges = base_price * 0.12
        subtotal = base_price + making_charges
        vat = subtotal * 0.05
        total = subtotal + vat
        
        return {
            'base_price': round(base_price, 2),
            'making_charges': round(making_charges, 2),
            'subtotal': round(subtotal, 2),
            'vat': round(vat, 2),
            'total': round(total, 2)
        }
    
    def calculate_sovereign_price_india(self, price_per_10gm):
        """
        Calculate 1 sovereign (8 grams) price for India
        Formula: (price/10 * 8) + 12% making + 3% GST on making + 5% GST on total
        """
        price_per_gram = price_per_10gm / 10
        base_price = price_per_gram * 8
        
        making_charges = base_price * 0.12
        making_gst = making_charges * 0.03
        subtotal = base_price + making_charges + making_gst
        gst = subtotal * 0.05
        total = subtotal + gst
        
        return {
            'base_price': round(base_price, 2),
            'making_charges': round(making_charges, 2),
            'making_gst': round(making_gst, 2),
            'subtotal': round(subtotal, 2),
            'gst': round(gst, 2),
            'total': round(total, 2)
        }
    
    def calculate_customs_duty(self, gold_value_inr, grams=8, channel='red'):
        """
        Calculate customs duty when bringing gold from UAE to India
        
        Args:
            gold_value_inr: Total gold value in INR (without making charges/GST)
            grams: Weight in grams
            channel: 'red' (6%) or 'green' (33%)
        """
        exemption = 50000
        
        if gold_value_inr <= exemption:
            return {
                'gold_value': gold_value_inr,
                'exemption': exemption,
                'taxable_amount': 0,
                'customs_duty': 0,
                'gst': 0,
                'total_duty': 0,
                'channel': channel
            }
        
        taxable_amount = gold_value_inr - exemption
        
        if channel == 'red':
            customs_rate = 0.06  # 6%
        else:
            customs_rate = 0.33  # 33%
        
        customs_duty = taxable_amount * customs_rate
        customs_duty_rounded = math.ceil(customs_duty / 50) * 50  # Round to nearest 50
        
        # GST is optional (5% of customs duty)
        gst = customs_duty_rounded * 0.05
        
        return {
            'gold_value': gold_value_inr,
            'exemption': exemption,
            'taxable_amount': taxable_amount,
            'customs_duty': customs_duty_rounded,
            'gst': round(gst, 2),
            'total_duty_with_gst': customs_duty_rounded + gst,
            'total_duty_without_gst': customs_duty_rounded,
            'channel': channel.upper()
        }
    
    def generate_report(self):
        """Generate comprehensive price report"""
        report = {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'sources': {},
            'calculations': {}
        }
        
        # Add source prices
        for source, data in self.prices.items():
            report['sources'][source] = data
        
        # Calculate sovereign prices for UAE sources
        for source in ['goldapi', 'kalyan', 'joy_alukkas', 'bhima']:
            if source in self.prices:
                prices_22k = self.prices[source]['prices'].get('22k', 0)
                if prices_22k:
                    calc = self.calculate_sovereign_price_uae(prices_22k)
                    report['calculations'][f'{source}_22k_sovereign'] = calc
        
        # Calculate sovereign prices for India
        if 'candere' in self.prices:
            price_22k = self.prices['candere']['prices'].get('22k', 0)
            if price_22k:
                calc = self.calculate_sovereign_price_india(price_22k)
                report['calculations']['candere_22k_sovereign'] = calc
                
                # Calculate customs duties
                base_price = calc['base_price']
                report['calculations']['customs_red_8g'] = self.calculate_customs_duty(base_price, 8, 'red')
                report['calculations']['customs_green_8g'] = self.calculate_customs_duty(base_price, 8, 'green')
                report['calculations']['customs_red_16g'] = self.calculate_customs_duty(base_price * 2, 16, 'red')
                report['calculations']['customs_green_16g'] = self.calculate_customs_duty(base_price * 2, 16, 'green')
        
        return report
    
    def send_email_notification(self, report):
        """Send email with price report"""
        print("\n📧 Sending email notification...")
        
        try:
            # Use config email settings if available
            email_config = self.config.get('email', {})
            sender = email_config.get('sender', self.gmail_config['sender_email'])
            password = email_config.get('password', self.gmail_config['sender_password'])
            recipient = email_config.get('recipient', self.gmail_config['recipient'])
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Gold Price Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            msg['From'] = sender
            msg['To'] = recipient
            
            # Create HTML email
            html = self.format_email_html(report)
            msg.attach(MIMEText(html, 'html'))
            
            # Send email
            with smtplib.SMTP(self.gmail_config['smtp_server'], self.gmail_config['smtp_port']) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
            
            print(f"   ✅ Email sent to {recipient}")
            return True
        
        except Exception as e:
            print(f"   ❌ Error sending email: {e}")
            return False
    
    def format_email_html(self, report):
        """Format report as HTML email"""
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2563eb; }}
                h2 {{ color: #1e40af; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #2563eb; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
                .highlight {{ background-color: #fef3c7; font-weight: bold; }}
                .section {{ margin: 30px 0; }}
            </style>
        </head>
        <body>
            <h1>🏅 Gold Price Report</h1>
            <p><strong>Generated:</strong> {report['timestamp']}</p>
            
            <div class="section">
                <h2>📊 Current Prices - UAE</h2>
                <table>
                    <tr>
                        <th>Source</th>
                        <th>24K (AED/gm)</th>
                        <th>22K (AED/gm)</th>
                        <th>18K (AED/gm)</th>
                    </tr>
        """
        
        # Add UAE sources
        for source in ['goldapi', 'kalyan', 'joy_alukkas', 'bhima']:
            if source in report['sources']:
                prices = report['sources'][source]['prices']
                source_name = source.replace('_', ' ').title()
                if source == 'goldapi':
                    source_name = 'GoldAPI (Live Market)'
                html += f"""
                    <tr>
                        <td><strong>{source_name}</strong></td>
                        <td>{prices.get('24k', 'N/A')}</td>
                        <td>{prices.get('22k', 'N/A')}</td>
                        <td>{prices.get('18k', 'N/A')}</td>
                    </tr>
                """
        
        html += """
                </table>
            </div>
        """
        
        # Add India prices
        if 'candere' in report['sources']:
            prices = report['sources']['candere']['prices']
            html += f"""
            <div class="section">
                <h2>📊 Current Prices - India (Kerala)</h2>
                <table>
                    <tr>
                        <th>Source</th>
                        <th>24K (INR/10gm)</th>
                        <th>22K (INR/10gm)</th>
                    </tr>
                    <tr>
                        <td><strong>Candere</strong></td>
                        <td>₹{prices.get('24k', 'N/A')}</td>
                        <td>₹{prices.get('22k', 'N/A')}</td>
                    </tr>
                </table>
            </div>
            """
        
        # Add sovereign price calculations
        html += """
            <div class="section">
                <h2>💰 1 Sovereign (8 grams) Price - 22K Gold</h2>
                <h3>UAE Prices (including making charges + VAT)</h3>
                <table>
                    <tr>
                        <th>Source</th>
                        <th>Base Price</th>
                        <th>Making (12%)</th>
                        <th>VAT (5%)</th>
                        <th class="highlight">Total</th>
                    </tr>
        """
        
        for source in ['goldapi', 'kalyan', 'joy_alukkas', 'bhima']:
            key = f'{source}_22k_sovereign'
            if key in report['calculations']:
                calc = report['calculations'][key]
                source_name = source.replace('_', ' ').title()
                if source == 'goldapi':
                    source_name = 'GoldAPI (Live Market)'
                html += f"""
                    <tr>
                        <td><strong>{source_name}</strong></td>
                        <td>AED {calc['base_price']}</td>
                        <td>AED {calc['making_charges']}</td>
                        <td>AED {calc['vat']}</td>
                        <td class="highlight">AED {calc['total']}</td>
                    </tr>
                """
        
        html += """
                </table>
        """
        
        # Add India sovereign price
        if 'candere_22k_sovereign' in report['calculations']:
            calc = report['calculations']['candere_22k_sovereign']
            html += f"""
                <h3>India Price (including making charges + GST)</h3>
                <table>
                    <tr>
                        <th>Source</th>
                        <th>Base Price</th>
                        <th>Making (12%)</th>
                        <th>Making GST (3%)</th>
                        <th>GST (5%)</th>
                        <th class="highlight">Total</th>
                    </tr>
                    <tr>
                        <td><strong>Candere (Kerala)</strong></td>
                        <td>₹{calc['base_price']}</td>
                        <td>₹{calc['making_charges']}</td>
                        <td>₹{calc['making_gst']}</td>
                        <td>₹{calc['gst']}</td>
                        <td class="highlight">₹{calc['total']}</td>
                    </tr>
                </table>
            </div>
            """
        
        # Add customs duty calculations
        if 'customs_red_8g' in report['calculations']:
            html += """
            <div class="section">
                <h2>🛃 Customs Duty Calculator</h2>
                <p>When bringing gold from UAE to India</p>
                
                <h3>For 8 grams (1 Sovereign)</h3>
                <table>
                    <tr>
                        <th>Channel</th>
                        <th>Gold Value</th>
                        <th>Exemption</th>
                        <th>Taxable Amount</th>
                        <th>Duty Rate</th>
                        <th class="highlight">Customs Duty</th>
                    </tr>
            """
            
            for channel in ['red', 'green']:
                key = f'customs_{channel}_8g'
                if key in report['calculations']:
                    calc = report['calculations'][key]
                    rate = '6%' if channel == 'red' else '33%'
                    html += f"""
                        <tr>
                            <td><strong>{calc['channel']} Channel</strong></td>
                            <td>₹{calc['gold_value']}</td>
                            <td>₹{calc['exemption']}</td>
                            <td>₹{calc['taxable_amount']}</td>
                            <td>{rate}</td>
                            <td class="highlight">₹{calc['customs_duty']}</td>
                        </tr>
                    """
            
            html += """
                </table>
                
                <h3>For 16 grams (2 Sovereigns)</h3>
                <table>
                    <tr>
                        <th>Channel</th>
                        <th>Gold Value</th>
                        <th>Exemption</th>
                        <th>Taxable Amount</th>
                        <th>Duty Rate</th>
                        <th class="highlight">Customs Duty</th>
                    </tr>
            """
            
            for channel in ['red', 'green']:
                key = f'customs_{channel}_16g'
                if key in report['calculations']:
                    calc = report['calculations'][key]
                    rate = '6%' if channel == 'red' else '33%'
                    html += f"""
                        <tr>
                            <td><strong>{calc['channel']} Channel</strong></td>
                            <td>₹{calc['gold_value']}</td>
                            <td>₹{calc['exemption']}</td>
                            <td>₹{calc['taxable_amount']}</td>
                            <td>{rate}</td>
                            <td class="highlight">₹{calc['customs_duty']}</td>
                        </tr>
                    """
            
            html += """
                </table>
                <p><small>Note: GST on customs duty (5%) is optional and depends on customs officer</small></p>
            </div>
            """
        
        html += """
            <div class="section">
                <p><small>This report is auto-generated. Prices are fetched in real-time and may vary.</small></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def run(self):
        """Main execution"""
        print(f"\n{'='*70}")
        print(f"  GOLD PRICE TRACKER - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # Fetch live API prices first (fast and reliable)
        if self.config['sources'].get('goldapi', True):
            self.fetch_goldapi_prices()
        
        # Fetch prices from all sources
        if self.config['sources'].get('kalyan', True):
            self.fetch_kalyan_prices()
        
        if self.config['sources'].get('joy_alukkas', True):
            self.fetch_joy_alukkas_prices()
        
        if self.config['sources'].get('bhima', True):
            self.fetch_bhima_prices()
        
        if self.config['sources'].get('candere', True):
            self.fetch_candere_prices()
        
        # Generate report
        report = self.generate_report()
        
        # Save report to JSON
        report_file = f"reports/gold_report_{self.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs('reports', exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"\n💾 Report saved: {report_file}")
        
        # Send email notification
        self.send_email_notification(report)
        
        print(f"\n{'='*70}")
        print("  ✅ TRACKING COMPLETE")
        print(f"{'='*70}\n")
        
        return report


if __name__ == "__main__":
    tracker = GoldPriceTracker()
    tracker.run()

