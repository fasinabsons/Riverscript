# 🏅 KaratMate Labs

**Professional Gold Price Tracking and Analysis System**

## Overview

KaratMate Labs is a comprehensive gold price tracking system that fetches live gold prices from multiple UAE and India sources, performs sovereign price calculations, and calculates customs duty for gold imports.

## Features

- ✅ **Live Price Fetching** - Real-time gold prices from UAE and India sources
- ✅ **Sovereign Calculations** - Accurate pricing for 8g, 16g, and 20g gold
- ✅ **Customs Calculator** - Red Channel (6%) and Green Channel (33%) calculations
- ✅ **Email Reports** - Automated HTML email reports with all calculations
- ✅ **Modern UI** - React-based frontend with real-time updates
- ✅ **API Server** - RESTful API with CORS support

## Tech Stack

- **Backend:** Python 3.x, Flask, BeautifulSoup4
- **Frontend:** React, Vite
- **Email:** SMTP (Gmail)
- **Scraping:** Requests, BeautifulSoup

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python price_fetcher_api.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Quick Start

### Option 1: One-Click Start
```bash
START_KARATMETER.bat
```

### Option 2: Manual Start
**Terminal 1:**
```bash
cd backend
python price_fetcher_api.py
```

**Terminal 2:**
```bash
cd frontend
npm run dev
```

## API Endpoints

- `GET /api/health` - Health check
- `GET /api/fetch/all` - Fetch all prices and calculations
- `GET /api/fetch/sourcea` - Fetch UAE source
- `GET /api/fetch/sourceb` - Fetch India source
- `POST /api/fetch-and-email` - Fetch prices and send email

## Configuration

### Email Settings
Edit `backend/price_fetcher_api.py`:
```python
DEFAULT_EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'sender_email': 'your_email@gmail.com',
    'app_password': 'your_app_password',
    'recipient_email': 'recipient@gmail.com'
}
```

## Calculations

### UAE Pricing
- Base Price = Gold rate × Grams
- Making Charges = 8% (average, can be higher)
- VAT = 5% on subtotal
- **Total = Base + Making + VAT**

### India Pricing
- Base Price = (Price per 10gm ÷ 10) × Grams
- Making Charges = 12% (minimum)
- Making GST = 3% of making charges
- GST = 5% on subtotal
- **Total = Base + Making + Making GST + GST**

### Customs Duty
- **Exemption:** ₹50,000
- **Red Channel:** 6% (after exemption)
- **Green Channel:** 33% (after exemption)
- **Rounding:** Nearest ₹50
- **Optional GST:** 5% on customs duty

## Project Structure

```
gold_price_tracker/
├── backend/
│   ├── price_fetcher_api.py    # Main API server
│   ├── gold_tracker.py          # Legacy tracker
│   ├── config.json              # Configuration
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main React component
│   │   ├── karatmeter.js       # JavaScript client library
│   │   └── App.css             # Styles
│   └── package.json            # Node dependencies
├── START_KARATMETER.bat        # One-click start script
├── FETCH_AND_EMAIL.bat         # Email automation script
└── README.md                   # This file
```

## Scheduling

### Windows Task Scheduler
1. Open Task Scheduler
2. Create New Task
3. Set Trigger: Daily at 8:30 PM UAE Time
4. Set Action: Run `FETCH_AND_EMAIL.bat`

## Security Notes

⚠️ **Important:**
- Never commit email passwords to version control
- Use environment variables for sensitive data
- Keep API credentials secure
- Update `.gitignore` for sensitive files

## License

Private Project - All Rights Reserved

## Support

For issues or questions, please contact the development team.

---

**🏅 Powered by KaratMate Labs**  
*Professional Gold Price Analytics*
