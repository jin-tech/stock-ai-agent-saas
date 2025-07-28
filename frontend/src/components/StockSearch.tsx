'use client'

import { useState } from 'react';

interface StockSearchProps {
  onStockSearch: (symbol: string) => void;
}

export default function StockSearch({ onStockSearch }: StockSearchProps) {
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!symbol.trim()) {
      setErrorMessage('Please enter a stock symbol');
      return;
    }

    setLoading(true);
    try {
      await onStockSearch(symbol.trim().toUpperCase());
      setSymbol(''); // Clear the input after successful search
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Convert to uppercase and limit to 10 characters
    const value = e.target.value.toUpperCase().slice(0, 10);
    setSymbol(value);
  };

  const popularStocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX'];

  const handlePopularStockClick = (stockSymbol: string) => {
    setSymbol(stockSymbol);
  };

  return (
    <div className="space-y-4">
      {/* Search Form */}
      <form onSubmit={handleSubmit} className="flex gap-3">
        <div className="flex-1">
          <input
            type="text"
            value={symbol}
            onChange={handleInputChange}
            placeholder="Enter stock symbol (e.g., AAPL, GOOGL)"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
            disabled={loading}
          />
        </div>
        <button
          type="submit"
          disabled={loading || !symbol.trim()}
          className="px-6 py-2 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <span className="flex items-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Searching...
            </span>
          ) : (
            'Search'
          )}
        </button>
      </form>

      {/* Popular Stocks */}
      <div>
        <p className="text-sm text-gray-600 mb-2">Popular stocks:</p>
        <div className="flex flex-wrap gap-2">
          {popularStocks.map((stockSymbol) => (
            <button
              key={stockSymbol}
              onClick={() => handlePopularStockClick(stockSymbol)}
              disabled={loading}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:ring-2 focus:ring-primary-500 focus:ring-offset-1 disabled:opacity-50 transition-colors"
            >
              {stockSymbol}
            </button>
          ))}
        </div>
      </div>

      {/* Help Text */}
      <div className="text-xs text-gray-500">
        <p>
          💡 Enter any valid stock symbol (e.g., AAPL for Apple, GOOGL for Google). 
          Data is provided by Alpha Vantage API with some rate limiting.
        </p>
      </div>
    </div>
  );
}