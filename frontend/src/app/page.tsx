'use client'

import { useState, useEffect } from 'react'
import PERatioCard from '../components/PERatioCard'
import StockSearch from '../components/StockSearch'

// Types
interface StockInfo {
  symbol: string;
  company_name: string | null;
  pe_ratio: number | null;
  price: number | null;
  earnings_per_share: number | null;
  market_cap: string | null;
  last_updated: string;
  error?: string;
}

// Sample popular stocks for demonstration
const POPULAR_STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA'];

export default function Home() {
  const [stocks, setStocks] = useState<StockInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPopularStocks();
  }, []);

  const loadPopularStocks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load popular stocks PE ratios
      const response = await fetch(`/api/pe-ratios/batch?symbols=${POPULAR_STOCKS.join(',')}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch stock data');
      }
      
      const data = await response.json();
      setStocks(data.symbols || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error loading stocks:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStockSearch = async (symbol: string) => {
    try {
      const response = await fetch(`/api/stock-info/${symbol.toUpperCase()}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch stock data');
      }
      
      const stockData: StockInfo = await response.json();
      
      // Add to stocks list if not already present
      setStocks(prevStocks => {
        const existingIndex = prevStocks.findIndex(s => s.symbol === stockData.symbol);
        if (existingIndex >= 0) {
          // Update existing stock
          const newStocks = [...prevStocks];
          newStocks[existingIndex] = stockData;
          return newStocks;
        } else {
          // Add new stock at the beginning
          return [stockData, ...prevStocks];
        }
      });
    } catch (err) {
      console.error('Error searching stock:', err);
      alert('Error fetching stock data. Please try again.');
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          PE Ratio Dashboard
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Track and analyze Price-to-Earnings ratios for your favorite stocks. 
          Get real-time financial data and make informed investment decisions.
        </p>
      </div>

      {/* Search Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          Search Stocks
        </h2>
        <StockSearch onStockSearch={handleStockSearch} />
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <div className="text-3xl font-bold text-primary-600">{stocks.length}</div>
          <div className="text-gray-600">Stocks Tracked</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <div className="text-3xl font-bold text-success">
            {stocks.filter(s => s.pe_ratio && s.pe_ratio > 0).length}
          </div>
          <div className="text-gray-600">With PE Data</div>
        </div>
        <div className="bg-white rounded-lg shadow-md p-6 text-center">
          <div className="text-3xl font-bold text-warning">
            {stocks.filter(s => s.error).length}
          </div>
          <div className="text-gray-600">Data Errors</div>
        </div>
      </div>

      {/* PE Ratios Section */}
      <div>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-900">
            Stock PE Ratios
          </h2>
          <button
            onClick={loadPopularStocks}
            disabled={loading}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>

        {loading && stocks.length === 0 ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading stock data...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-700">Error: {error}</p>
            <button
              onClick={loadPopularStocks}
              className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        ) : stocks.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-600">No stock data available. Search for a stock above.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stocks.map((stock) => (
              <PERatioCard key={stock.symbol} stock={stock} />
            ))}
          </div>
        )}
      </div>

      {/* Information Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          About PE Ratios
        </h3>
        <p className="text-blue-700">
          The Price-to-Earnings ratio (P/E) is a valuation metric that compares a company's current share price 
          to its earnings per share. A lower P/E might indicate that the stock is undervalued, while a higher 
          P/E might suggest overvaluation. However, P/E ratios should be compared within the same industry for 
          meaningful analysis.
        </p>
      </div>
    </div>
  )
}
