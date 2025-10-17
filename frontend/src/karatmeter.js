/**
 * KaratMate Labs - Live Gold Price Fetcher
 * Browser-based price fetching with real-time updates
 */

const KARATMATE_API = 'http://localhost:5002';

class KaratMateLabs {
  constructor() {
    this.prices = {};
    this.lastUpdate = null;
    console.log('🏅 KaratMate Labs - Initialized');
  }

  /**
   * Fetch Source A prices
   */
  async fetchSourceA() {
    console.log('\n📊 [KaratMate Labs] Fetching KaratMate UAE (Source A) prices...');
    
    try{
      const response = await fetch(`${KARATMATE_API}/api/fetch/sourcea`);
      const data = await response.json();
      
      if (data.success) {
        console.log(`✅ [KaratMate Labs] KaratMate UAE:`, data.prices);
        console.log(`   24K: ${data.prices['24k']} AED/gram`);
        console.log(`   22K: ${data.prices['22k']} AED/gram`);
        console.log(`   18K: ${data.prices['18k']} AED/gram`);
        
        this.prices.sourcea = data;
        return data;
      } else {
        console.error('❌ [KaratMate Labs] Failed to fetch KaratMate UAE:', data.error);
        return null;
      }
    } catch (error) {
      console.error('❌ [KaratMate Labs] Error fetching KaratMate UAE:', error);
      return null;
    }
  }

  /**
   * Fetch Source B prices
   */
  async fetchSourceB() {
    console.log('\n📊 [KaratMate Labs] Fetching KaratMate India (Source B) prices...');
    
    try {
      const response = await fetch(`${KARATMATE_API}/api/fetch/sourceb`);
      const data = await response.json();
      
      if (data.success) {
        console.log(`✅ [KaratMate Labs] KaratMate India:`, data.prices);
        console.log(`   24K: ₹${data.prices['24k']}/10gm`);
        console.log(`   22K: ₹${data.prices['22k']}/10gm`);
        
        this.prices.sourceb = data;
        return data;
      } else {
        console.error('❌ [KaratMate Labs] Failed to fetch KaratMate India:', data.error);
        return null;
      }
    } catch (error) {
      console.error('❌ [KaratMate Labs] Error fetching KaratMate India:', error);
      return null;
    }
  }

  /**
   * Fetch all prices
   */
  async fetchAll() {
    console.log('\n' + '='.repeat(60));
    console.log('  🏅 KaratMate Labs - Live Price Fetch');
    console.log('='.repeat(60));
    
    try {
      const response = await fetch(`${KARATMATE_API}/api/fetch/all`);
      const data = await response.json();
      
      if (data.success) {
        this.prices = data.sources;
        this.lastUpdate = new Date(data.timestamp);
        
        console.log('\n✅ [KaratMate Labs] All prices fetched successfully!\n');
        
        // Display Source A
        if (data.sources.sourcea) {
          const ja = data.sources.sourcea;
          console.log('📍 KARATMATE UAE (Source A)');
          console.log(`   24K: ${ja.prices['24k']} AED/gram`);
          console.log(`   22K: ${ja.prices['22k']} AED/gram`);
          console.log(`   18K: ${ja.prices['18k']} AED/gram`);
        }
        
        // Display Source B
        if (data.sources.sourceb) {
          const ca = data.sources.sourceb;
          console.log('\n📍 KARATMATE INDIA (Source B Kerala)');
          console.log(`   24K: ₹${ca.prices['24k']}/10gm`);
          console.log(`   22K: ₹${ca.prices['22k']}/10gm`);
        }
        
        console.log('\n' + '='.repeat(60));
        console.log(`  Last Updated: ${this.lastUpdate.toLocaleString()}`);
        console.log('='.repeat(60) + '\n');
        
        return data;
      } else {
        console.error('❌ [KaratMate Labs] Failed to fetch prices');
        return null;
      }
    } catch (error) {
      console.error('❌ [KaratMate Labs] Error fetching all prices:', error);
      return null;
    }
  }

  /**
   * Calculate sovereign price (8 grams)
   */
  calculateSovereignUAE(pricePerGram, grams = 8) {
    const basePrice = pricePerGram * grams;
    const makingCharges = basePrice * 0.08; // 8% (average, can be higher)
    const subtotal = basePrice + makingCharges;
    const vat = basePrice * 0.05; // 5% on subtotal
    const total = subtotal + vat;
    
    return {
      basePrice: Math.round(basePrice * 100) / 100,
      makingCharges: Math.round(makingCharges * 100) / 100,
      vat: Math.round(vat * 100) / 100,
      total: Math.round(total * 100) / 100,
      grams: grams
    };
  }

  calculateSovereignIndia(pricePer10gm, grams = 8) {
    const pricePerGram = pricePer10gm / 10;
    const basePrice = pricePerGram * grams;
    const makingCharges = basePrice * 0.12; // 12% (minimum)
    const makingGST = makingCharges * 0.03; // 3%
    const subtotal = basePrice + makingCharges + makingGST;
    const gst = basePrice * 0.05; // 5% on subtotal
    const total = subtotal + gst;
    
    return {
      basePrice: Math.round(basePrice * 100) / 100,
      makingCharges: Math.round(makingCharges * 100) / 100,
      makingGST: Math.round(makingGST * 100) / 100,
      gst: Math.round(gst * 100) / 100,
      total: Math.round(total * 100) / 100,
      grams: grams
    };
  }

  /**
   * Get current prices
   */
  getPrices() {
    return {
      prices: this.prices,
      lastUpdate: this.lastUpdate,
      provider: 'KaratMate Labs'
    };
  }
}

// Export for use in React
if (typeof module !== 'undefined' && module.exports) {
  module.exports = KaratMateLabs;
}

// Make available globally
if (typeof window !== 'undefined') {
  window.KaratMateLabs = KaratMateLabs;
}

export default KaratMateLabs;

