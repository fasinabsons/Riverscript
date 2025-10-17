import React, { useState, useEffect } from 'react';
import './App.css';
import KaratMeterLabs from './karatmeter.js';

const API_URL = 'http://localhost:5001';
const KARATMETER_API = 'http://localhost:5002';

function App() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('prices');
  const [report, setReport] = useState(null);
  const [reports, setReports] = useState([]);
  const [karatMeterPrices, setKaratMeterPrices] = useState(null);

  useEffect(() => {
    loadConfig();
    loadReports();
    
    // Initialize KaratMeter Labs
    window.karatMeter = new KaratMeterLabs();
    console.log('🏅 KaratMeter Labs initialized and available as window.karatMeter');
  }, []);

  const loadConfig = async () => {
    try {
      const response = await fetch(`${API_URL}/api/config`);
      const data = await response.json();
      if (data.success) {
        setConfig(data.config);
      }
    } catch (error) {
      showMessage('Error loading configuration', 'error');
    }
  };

  const loadReports = async () => {
    try {
      const response = await fetch(`${API_URL}/api/reports`);
      const data = await response.json();
      if (data.success) {
        setReports(data.reports);
      }
    } catch (error) {
      console.error('Error loading reports:', error);
    }
  };

  const saveConfig = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      const data = await response.json();
      
      if (data.success) {
        showMessage('✅ Configuration saved successfully!', 'success');
      } else {
        showMessage(`❌ Error: ${data.error}`, 'error');
      }
    } catch (error) {
      showMessage(`❌ Error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchPrices = async () => {
    try {
      setLoading(true);
      showMessage('📊 Fetching gold prices from all sources...', 'info');
      
      const response = await fetch(`${API_URL}/api/fetch-prices`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.success) {
        setReport(data.report);
        showMessage('✅ Prices fetched successfully!', 'success');
        loadReports(); // Refresh reports list
      } else {
        showMessage(`❌ Error: ${data.error}`, 'error');
      }
    } catch (error) {
      showMessage(`❌ Error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchKaratMeterPrices = async () => {
    try {
      setLoading(true);
      showMessage('🏅 [KaratMeter Labs] Fetching live prices...', 'info');
      
      console.log('\n' + '='.repeat(60));
      console.log('  🏅 KaratMeter Labs - Live Price Fetch');
      console.log('='.repeat(60));
      
      const response = await fetch(`${KARATMETER_API}/api/fetch/all`);
      const data = await response.json();
      
      if (data.success) {
        setKaratMeterPrices(data);
        
        // Log to console
        console.log('\n✅ [KaratMeter Labs] All prices fetched successfully!\n');
        
        if (data.sources.joyalukkas) {
          const ja = data.sources.joyalukkas;
          console.log('📍 JOY ALUKKAS (UAE)');
          console.log(`   24K: ${ja.prices['24k']} AED/gram`);
          console.log(`   22K: ${ja.prices['22k']} AED/gram`);
          console.log(`   18K: ${ja.prices['18k']} AED/gram`);
        }
        
        if (data.sources.candere) {
          const ca = data.sources.candere;
          console.log('\n📍 CANDERE (Kerala, India)');
          console.log(`   24K: ₹${ca.prices['24k']}/10gm`);
          console.log(`   22K: ₹${ca.prices['22k']}/10gm`);
        }
        
        console.log('\n' + '='.repeat(60));
        console.log(`  Powered by KaratMeter Labs`);
        console.log('='.repeat(60) + '\n');
        
        showMessage('✅ [KaratMeter Labs] Live prices fetched successfully!', 'success');
      } else {
        showMessage(`❌ [KaratMeter Labs] Error: ${data.error}`, 'error');
      }
    } catch (error) {
      showMessage(`❌ [KaratMeter Labs] Error: ${error.message}`, 'error');
      console.error('❌ [KaratMeter Labs] Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendTestEmail = async () => {
    try {
      setLoading(true);
      showMessage('📧 Sending test email...', 'info');
      
      const response = await fetch(`${API_URL}/api/send-test-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config.email)
      });
      const data = await response.json();
      
      if (data.success) {
        showMessage('✅ Test email sent successfully!', 'success');
      } else {
        showMessage(`❌ Error: ${data.error}`, 'error');
      }
    } catch (error) {
      showMessage(`❌ Error: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (msg, type) => {
    setMessage({ text: msg, type });
    setTimeout(() => setMessage(''), 5000);
  };

  const updateEmailConfig = (field, value) => {
    setConfig({
      ...config,
      email: { ...config.email, [field]: value }
    });
  };

  const toggleSource = (source) => {
    setConfig({
      ...config,
      sources: { ...config.sources, [source]: !config.sources[source] }
    });
  };

  if (!config) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="App">
      <header className="header">
        <div className="container">
          <h1>🏅 Gold Price Tracker</h1>
          <p>Real-time gold prices from UAE & India with customs calculator</p>
        </div>
      </header>

      <nav className="nav">
        <button 
          className={activeTab === 'prices' ? 'active' : ''} 
          onClick={() => setActiveTab('prices')}
        >
          📊 Prices
        </button>
        <button 
          className={activeTab === 'settings' ? 'active' : ''} 
          onClick={() => setActiveTab('settings')}
        >
          ⚙️ Settings
        </button>
        <button 
          className={activeTab === 'history' ? 'active' : ''} 
          onClick={() => setActiveTab('history')}
        >
          📈 History
        </button>
      </nav>

      <main className="main">
        <div className="container">
          {message && (
            <div className={`message ${message.type}`}>
              {message.text}
            </div>
          )}

          {activeTab === 'prices' && (
            <div className="tab-content">
              <div className="card" style={{background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white'}}>
                <h2 style={{color: 'white'}}>🏅 KaratMeter Labs - Live Price Fetcher</h2>
                <p style={{color: 'rgba(255,255,255,0.9)'}}>Fetch real-time gold prices from Joy Alukkas (UAE) and Candere (India)</p>
                
                <button 
                  className="btn btn-large" 
                  style={{background: 'white', color: '#667eea', fontWeight: 'bold'}}
                  onClick={fetchKaratMeterPrices}
                  disabled={loading}
                >
                  {loading ? '⏳ Fetching Live Prices...' : '🏅 Fetch Live Prices (KaratMeter Labs)'}
                </button>
              </div>

              {karatMeterPrices && (
                <>
                  <div className="card">
                    <h2>🏅 KaratMeter Labs - Live Prices</h2>
                    <p className="live-indicator">🔴 LIVE DATA</p>
                    
                    <div className="price-grid">
                      {karatMeterPrices.sources.joyalukkas && (
                        <div className="price-card">
                          <h3>JOY ALUKKAS (UAE)</h3>
                          <span className="live-badge">🔴 LIVE</span>
                          <div className="prices">
                            <div className="price-item">
                              <span className="label">24K:</span>
                              <span className="value">AED {karatMeterPrices.sources.joyalukkas.prices['24k']}/gram</span>
                            </div>
                            <div className="price-item">
                              <span className="label">22K:</span>
                              <span className="value">AED {karatMeterPrices.sources.joyalukkas.prices['22k']}/gram</span>
                            </div>
                            <div className="price-item">
                              <span className="label">18K:</span>
                              <span className="value">AED {karatMeterPrices.sources.joyalukkas.prices['18k']}/gram</span>
                            </div>
                          </div>
                        </div>
                      )}

                      {karatMeterPrices.sources.candere && (
                        <div className="price-card">
                          <h3>CANDERE (Kerala, India)</h3>
                          <span className="live-badge">🔴 LIVE</span>
                          <div className="prices">
                            <div className="price-item">
                              <span className="label">24K:</span>
                              <span className="value">₹{karatMeterPrices.sources.candere.prices['24k']}/10gm</span>
                            </div>
                            <div className="price-item">
                              <span className="label">22K:</span>
                              <span className="value">₹{karatMeterPrices.sources.candere.prices['22k']}/10gm</span>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    <p style={{textAlign: 'center', marginTop: '20px', color: '#666', fontSize: '14px'}}>
                      Powered by <strong>KaratMeter Labs</strong> | Last Updated: {new Date(karatMeterPrices.timestamp).toLocaleString()}
                    </p>
                  </div>
                </>
              )}

              <div className="card">
                <h2>Legacy Fetch (Old Method)</h2>
                <p>Click the button below to fetch using the old Selenium-based method</p>
                
                <button 
                  className="btn btn-secondary btn-large" 
                  onClick={fetchPrices}
                  disabled={loading}
                >
                  {loading ? '⏳ Fetching Prices...' : '⚡ Fetch Gold Prices (Old Method)'}
                </button>
              </div>

              {report && (
                <>
                  <div className="card">
                    <h2>🌍 UAE & International Prices (per gram)</h2>
                    <div className="price-grid">
                      {['goldapi', 'kalyan', 'joy_alukkas', 'bhima'].map(source => (
                        report.sources[source] && (
                          <div key={source} className="price-card">
                            <h3>{source === 'goldapi' ? '🌐 GOLDAPI (LIVE MARKET)' : source.replace('_', ' ').toUpperCase()}</h3>
                            {source === 'goldapi' && <span className="live-badge">🔴 LIVE</span>}
                            <div className="prices">
                              <div className="price-item">
                                <span className="label">24K:</span>
                                <span className="value">AED {report.sources[source].prices['24k'] || 'N/A'}</span>
                              </div>
                              <div className="price-item">
                                <span className="label">22K:</span>
                                <span className="value">AED {report.sources[source].prices['22k'] || 'N/A'}</span>
                              </div>
                              <div className="price-item">
                                <span className="label">18K:</span>
                                <span className="value">AED {report.sources[source].prices['18k'] || 'N/A'}</span>
                              </div>
                            </div>
                          </div>
                        )
                      ))}
                    </div>
                  </div>

                  {report.sources.candere && (
                    <div className="card">
                      <h2>🇮🇳 India Prices (Kerala - per 10 grams)</h2>
                      <div className="price-card">
                        <h3>CANDERE</h3>
                        <div className="prices">
                          <div className="price-item">
                            <span className="label">24K:</span>
                            <span className="value">₹{report.sources.candere.prices['24k']}/10gm</span>
                          </div>
                          <div className="price-item">
                            <span className="label">22K:</span>
                            <span className="value">₹{report.sources.candere.prices['22k']}/10gm</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="card">
                    <h2>💰 1 Sovereign (8 grams) Price - 22K Gold</h2>
                    
                    <h3>UAE (with 12% making + 5% VAT)</h3>
                    <div className="calc-grid">
                      {['goldapi', 'kalyan', 'joy_alukkas', 'bhima'].map(source => {
                        const key = `${source}_22k_sovereign`;
                        if (report.calculations[key]) {
                          const calc = report.calculations[key];
                          const displayName = source === 'goldapi' ? '🌐 GOLDAPI (LIVE)' : source.replace('_', ' ').toUpperCase();
                          return (
                            <div key={source} className="calc-card">
                              <h4>{displayName}</h4>
                              <div className="calc-details">
                                <div className="calc-row">
                                  <span>Base Price:</span>
                                  <span>AED {calc.base_price}</span>
                                </div>
                                <div className="calc-row">
                                  <span>Making (12%):</span>
                                  <span>AED {calc.making_charges}</span>
                                </div>
                                <div className="calc-row">
                                  <span>VAT (5%):</span>
                                  <span>AED {calc.vat}</span>
                                </div>
                                <div className="calc-row total">
                                  <span>Total:</span>
                                  <span>AED {calc.total}</span>
                                </div>
                              </div>
                            </div>
                          );
                        }
                        return null;
                      })}
                    </div>

                    {report.calculations.candere_22k_sovereign && (
                      <>
                        <h3>India (with 12% making + 3% GST on making + 5% GST)</h3>
                        <div className="calc-card">
                          <h4>CANDERE (Kerala)</h4>
                          <div className="calc-details">
                            <div className="calc-row">
                              <span>Base Price:</span>
                              <span>₹{report.calculations.candere_22k_sovereign.base_price}</span>
                            </div>
                            <div className="calc-row">
                              <span>Making (12%):</span>
                              <span>₹{report.calculations.candere_22k_sovereign.making_charges}</span>
                            </div>
                            <div className="calc-row">
                              <span>Making GST (3%):</span>
                              <span>₹{report.calculations.candere_22k_sovereign.making_gst}</span>
                            </div>
                            <div className="calc-row">
                              <span>GST (5%):</span>
                              <span>₹{report.calculations.candere_22k_sovereign.gst}</span>
                            </div>
                            <div className="calc-row total">
                              <span>Total:</span>
                              <span>₹{report.calculations.candere_22k_sovereign.total}</span>
                            </div>
                          </div>
                        </div>
                      </>
                    )}
                  </div>

                  {report.calculations.customs_red_8g && (
                    <div className="card">
                      <h2>🛃 Customs Duty Calculator</h2>
                      <p>When bringing gold from UAE to India</p>

                      <h3>For 8 grams (1 Sovereign)</h3>
                      <div className="customs-grid">
                        {['red', 'green'].map(channel => {
                          const calc = report.calculations[`customs_${channel}_8g`];
                          return (
                            <div key={channel} className="customs-card">
                              <h4>{calc.channel} Channel ({channel === 'red' ? '6%' : '33%'})</h4>
                              <div className="calc-details">
                                <div className="calc-row">
                                  <span>Gold Value:</span>
                                  <span>₹{calc.gold_value}</span>
                                </div>
                                <div className="calc-row">
                                  <span>Exemption:</span>
                                  <span>-₹{calc.exemption}</span>
                                </div>
                                <div className="calc-row">
                                  <span>Taxable:</span>
                                  <span>₹{calc.taxable_amount}</span>
                                </div>
                                <div className="calc-row total">
                                  <span>Customs Duty:</span>
                                  <span>₹{calc.customs_duty}</span>
                                </div>
                                <div className="calc-row">
                                  <span>GST (Optional 5%):</span>
                                  <span>₹{calc.gst}</span>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>

                      <h3>For 16 grams (2 Sovereigns)</h3>
                      <div className="customs-grid">
                        {['red', 'green'].map(channel => {
                          const calc = report.calculations[`customs_${channel}_16g`];
                          return (
                            <div key={channel} className="customs-card">
                              <h4>{calc.channel} Channel ({channel === 'red' ? '6%' : '33%'})</h4>
                              <div className="calc-details">
                                <div className="calc-row">
                                  <span>Gold Value:</span>
                                  <span>₹{calc.gold_value}</span>
                                </div>
                                <div className="calc-row">
                                  <span>Exemption:</span>
                                  <span>-₹{calc.exemption}</span>
                                </div>
                                <div className="calc-row">
                                  <span>Taxable:</span>
                                  <span>₹{calc.taxable_amount}</span>
                                </div>
                                <div className="calc-row total">
                                  <span>Customs Duty:</span>
                                  <span>₹{calc.customs_duty}</span>
                                </div>
                                <div className="calc-row">
                                  <span>GST (Optional 5%):</span>
                                  <span>₹{calc.gst}</span>
                                </div>
                              </div>
                            </div>
                          );
                        })}
                      </div>

                      <p className="note">
                        <small>Note: GST on customs duty (5%) is optional and depends on customs officer</small>
                      </p>
                    </div>
                  )}
                </>
              )}
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="tab-content">
              <div className="card">
                <h2>Email Notification Settings</h2>
                
                <div className="form-group">
                  <label>Sender Email:</label>
                  <input 
                    type="email" 
                    value={config.email.sender}
                    onChange={(e) => updateEmailConfig('sender', e.target.value)}
                    placeholder="your-email@gmail.com"
                  />
                </div>

                <div className="form-group">
                  <label>App Password:</label>
                  <input 
                    type="password" 
                    value={config.email.password}
                    onChange={(e) => updateEmailConfig('password', e.target.value)}
                    placeholder="Your Gmail App Password"
                  />
                  <small>Generate App Password from your Google Account security settings</small>
                </div>

                <div className="form-group">
                  <label>Recipient Email:</label>
                  <input 
                    type="email" 
                    value={config.email.recipient}
                    onChange={(e) => updateEmailConfig('recipient', e.target.value)}
                    placeholder="recipient@gmail.com"
                  />
                </div>

                <div className="button-group">
                  <button className="btn btn-primary" onClick={saveConfig} disabled={loading}>
                    💾 Save Settings
                  </button>
                  <button className="btn btn-secondary" onClick={sendTestEmail} disabled={loading}>
                    📧 Send Test Email
                  </button>
                </div>
              </div>

              <div className="card">
                <h2>Data Sources</h2>
                <p>Select which sources to fetch prices from:</p>
                
                <div className="sources-grid">
                  <label className="checkbox-label">
                    <input 
                      type="checkbox" 
                      checked={config.sources.kalyan}
                      onChange={() => toggleSource('kalyan')}
                    />
                    <span>Kalyan Jewellers (UAE)</span>
                  </label>

                  <label className="checkbox-label">
                    <input 
                      type="checkbox" 
                      checked={config.sources.joy_alukkas}
                      onChange={() => toggleSource('joy_alukkas')}
                    />
                    <span>Joy Alukkas (UAE)</span>
                  </label>

                  <label className="checkbox-label">
                    <input 
                      type="checkbox" 
                      checked={config.sources.bhima}
                      onChange={() => toggleSource('bhima')}
                    />
                    <span>Bhima Jewellers (UAE)</span>
                  </label>

                  <label className="checkbox-label">
                    <input 
                      type="checkbox" 
                      checked={config.sources.candere}
                      onChange={() => toggleSource('candere')}
                    />
                    <span>Candere (India - Kerala)</span>
                  </label>

                  <label className="checkbox-label">
                    <input 
                      type="checkbox" 
                      checked={config.sources.goldapi}
                      onChange={() => toggleSource('goldapi')}
                    />
                    <span>🌐 GoldAPI (Live International Market)</span>
                  </label>
                </div>

                <button className="btn btn-primary" onClick={saveConfig} disabled={loading}>
                  💾 Save Settings
                </button>
              </div>

              <div className="card info-card">
                <h3>📧 About Gmail App Passwords</h3>
                <p><strong>Daily Email Limit:</strong> With Gmail App Password, you can send approximately 500 emails per day (Gmail's standard limit).</p>
                
                <h4>How to generate an App Password:</h4>
                <ol>
                  <li>Go to your Google Account settings</li>
                  <li>Navigate to Security → 2-Step Verification</li>
                  <li>Scroll to "App passwords"</li>
                  <li>Select "Mail" and your device</li>
                  <li>Copy the 16-character password</li>
                  <li>Paste it in the "App Password" field above</li>
                </ol>
              </div>
            </div>
          )}

          {activeTab === 'history' && (
            <div className="tab-content">
              <div className="card">
                <h2>Price History</h2>
                <p>Previous price reports:</p>
                
                {reports.length > 0 ? (
                  <div className="reports-list">
                    {reports.map(r => (
                      <div key={r.filename} className="report-item">
                        <span className="report-date">{r.timestamp}</span>
                        <span className="report-sources">{r.sources_count} sources</span>
                        <button className="btn btn-small">View</button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-data">No reports yet. Fetch prices to create your first report!</p>
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>🏅 Gold Price Tracker © 2024 | Updates daily at 8:30 PM UAE Time</p>
        </div>
      </footer>
    </div>
  );
}

export default App;

