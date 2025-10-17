"""
Gold Price Tracker - REST API Server
Provides endpoints for React frontend
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
from gold_tracker import GoldPriceTracker

app = Flask(__name__)
CORS(app)

CONFIG_FILE = 'config.json'


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        else:
            # Return default config
            config = {
                'sources': {
                    'kalyan': True,
                    'joy_alukkas': True,
                    'bhima': True,
                    'candere': True
                },
                'email': {
                    'sender': 'fasin.absons@gmail.com',
                    'password': '',  # Don't send password to frontend
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
        
        # Remove password before sending
        if 'email' in config and 'password' in config['email']:
            config['email']['password'] = ''
        
        return jsonify({'success': True, 'config': config})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        new_config = request.json
        
        # Load existing config
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Update config (only update provided fields)
        for key, value in new_config.items():
            if isinstance(value, dict) and key in config:
                config[key].update(value)
            else:
                config[key] = value
        
        # Save config
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        
        return jsonify({'success': True, 'message': 'Configuration updated'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fetch-prices', methods=['POST'])
def fetch_prices():
    """Fetch current gold prices"""
    try:
        tracker = GoldPriceTracker(CONFIG_FILE)
        report = tracker.run()
        
        return jsonify({'success': True, 'report': report})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reports', methods=['GET'])
def get_reports():
    """Get list of saved reports"""
    try:
        reports_dir = 'reports'
        if not os.path.exists(reports_dir):
            return jsonify({'success': True, 'reports': []})
        
        files = [f for f in os.listdir(reports_dir) if f.endswith('.json')]
        files.sort(reverse=True)  # Newest first
        
        reports = []
        for filename in files[:10]:  # Return last 10 reports
            filepath = os.path.join(reports_dir, filename)
            with open(filepath, 'r') as f:
                report = json.load(f)
                reports.append({
                    'filename': filename,
                    'timestamp': report.get('timestamp', ''),
                    'sources_count': len(report.get('sources', {}))
                })
        
        return jsonify({'success': True, 'reports': reports})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reports/<filename>', methods=['GET'])
def get_report(filename):
    """Get specific report"""
    try:
        filepath = os.path.join('reports', filename)
        if not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'Report not found'}), 404
        
        with open(filepath, 'r') as f:
            report = json.load(f)
        
        return jsonify({'success': True, 'report': report})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/send-test-email', methods=['POST'])
def send_test_email():
    """Send test email"""
    try:
        data = request.json
        
        # Update config temporarily for test
        config = {
            'email': {
                'sender': data.get('sender', 'fasin.absons@gmail.com'),
                'password': data.get('password', ''),
                'recipient': data.get('recipient', 'faseen1532@gmail.com')
            }
        }
        
        # Save temporary config
        with open('temp_config.json', 'w') as f:
            json.dump(config, f)
        
        # Create tracker with temp config
        tracker = GoldPriceTracker('temp_config.json')
        
        # Create simple test report
        test_report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'sources': {},
            'calculations': {}
        }
        
        # Send email
        success = tracker.send_email_notification(test_report)
        
        # Clean up
        if os.path.exists('temp_config.json'):
            os.remove('temp_config.json')
        
        if success:
            return jsonify({'success': True, 'message': 'Test email sent successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send email'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("\n🌐 Gold Price Tracker API Server")
    print("="*50)
    print("API available at: http://localhost:5001")
    print("Endpoints:")
    print("  GET  /api/health")
    print("  GET  /api/config")
    print("  POST /api/config")
    print("  POST /api/fetch-prices")
    print("  GET  /api/reports")
    print("  GET  /api/reports/<filename>")
    print("  POST /api/send-test-email")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)

