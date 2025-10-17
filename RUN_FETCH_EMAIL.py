"""
🏅 KaratMeter Labs - One-Click Fetch & Email Script
This script fetches live gold prices and sends email report
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from price_fetcher_api import fetch_all_internal, send_email_report

def main():
    print("\n" + "="*60)
    print("  🏅 KaratMeter Labs - Fetch & Email Script")
    print("="*60)
    print("\nFetching live gold prices...")
    print("This will take 5-10 seconds...\n")
    
    # Fetch all prices and calculations
    data = fetch_all_internal()
    
    if data['success']:
        print("\n✅ Prices fetched successfully!")
        print(f"\nSources found: {len(data['sources'])}")
        
        # Display prices
        if 'joyalukkas' in data['sources']:
            ja = data['sources']['joyalukkas']
            print(f"\n📍 Joy Alukkas (UAE):")
            print(f"   24K: {ja['prices'].get('24k')} AED/gram")
            print(f"   22K: {ja['prices'].get('22k')} AED/gram")
        
        if 'candere' in data['sources']:
            ca = data['sources']['candere']
            print(f"\n📍 Candere (Kerala, India):")
            print(f"   24K: ₹{ca['prices'].get('24k')}/10gm")
            print(f"   22K: ₹{ca['prices'].get('22k')}/10gm")
        
        # Send email
        print("\n📧 Sending email report...")
        email_sent = send_email_report(data)
        
        if email_sent:
            print("\n✅ Email sent successfully to: faseen1532@gmail.com")
            print("\nEmail contains:")
            print("  • Live gold prices from all sources")
            print("  • Sovereign calculations (8g & 16g)")
            print("  • Customs duty calculations (Red & Green)")
            print("  • All with beautiful HTML formatting")
        else:
            print("\n❌ Failed to send email. Check your email configuration.")
        
        print("\n" + "="*60)
        print("  Task Complete!")
        print("="*60 + "\n")
    else:
        print("\n❌ Failed to fetch prices. Check your internet connection.")
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()

