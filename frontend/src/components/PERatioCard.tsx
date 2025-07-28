'use client'

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

interface PERatioCardProps {
  stock: StockInfo;
}

export default function PERatioCard({ stock }: PERatioCardProps) {
  const formatPERatio = (peRatio: number | null) => {
    if (peRatio === null || peRatio === undefined) return 'N/A';
    return peRatio.toFixed(2);
  };

  const formatPrice = (price: number | null) => {
    if (price === null || price === undefined) return 'N/A';
    return `$${price.toFixed(2)}`;
  };

  const formatMarketCap = (marketCap: string | null) => {
    if (!marketCap || marketCap === 'N/A') return 'N/A';
    
    // Convert market cap to more readable format
    const num = parseInt(marketCap);
    if (num >= 1e12) return `$${(num / 1e12).toFixed(1)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(1)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(1)}M`;
    return `$${num.toLocaleString()}`;
  };

  const getPERatioClass = (peRatio: number | null) => {
    if (peRatio === null || peRatio === undefined) return 'text-gray-600';
    if (peRatio < 15) return 'text-green-600'; // Potentially undervalued
    if (peRatio > 30) return 'text-red-600';   // Potentially overvalued
    return 'text-blue-600';                    // Reasonable range
  };

  const getPERatioLabel = (peRatio: number | null) => {
    if (peRatio === null || peRatio === undefined) return 'No Data';
    if (peRatio < 15) return 'Low P/E';
    if (peRatio > 30) return 'High P/E';
    return 'Moderate P/E';
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Unknown';
    }
  };

  if (stock.error) {
    return (
      <div className="pe-ratio-card border-red-200 bg-red-50">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{stock.symbol}</h3>
            <p className="text-sm text-gray-600">Error loading data</p>
          </div>
          <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded">
            Error
          </span>
        </div>
        <div className="text-red-600 text-sm">
          {stock.error}
        </div>
        <div className="mt-4 text-xs text-gray-500">
          Last attempt: {formatDate(stock.last_updated)}
        </div>
      </div>
    );
  }

  return (
    <div className="pe-ratio-card">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{stock.symbol}</h3>
          <p className="text-sm text-gray-600">
            {stock.company_name || 'Unknown Company'}
          </p>
        </div>
        <span className={`text-xs font-medium px-2.5 py-0.5 rounded ${
          stock.pe_ratio !== null 
            ? 'bg-green-100 text-green-800' 
            : 'bg-gray-100 text-gray-800'
        }`}>
          {getPERatioLabel(stock.pe_ratio)}
        </span>
      </div>

      <div className="space-y-3">
        {/* PE Ratio */}
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">P/E Ratio:</span>
          <span className={`text-lg font-bold ${getPERatioClass(stock.pe_ratio)}`}>
            {formatPERatio(stock.pe_ratio)}
          </span>
        </div>

        {/* Stock Price */}
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Target Price:</span>
          <span className="text-sm text-gray-900 font-medium">
            {formatPrice(stock.price)}
          </span>
        </div>

        {/* Earnings Per Share */}
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">EPS:</span>
          <span className="text-sm text-gray-900 font-medium">
            {stock.earnings_per_share !== null 
              ? `$${stock.earnings_per_share.toFixed(2)}` 
              : 'N/A'}
          </span>
        </div>

        {/* Market Cap */}
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Market Cap:</span>
          <span className="text-sm text-gray-900 font-medium">
            {formatMarketCap(stock.market_cap)}
          </span>
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-gray-200 mt-4 pt-3">
        <div className="flex justify-between items-center text-xs text-gray-500">
          <span>Last updated:</span>
          <span>{formatDate(stock.last_updated)}</span>
        </div>
      </div>

      {/* PE Ratio Interpretation */}
      {stock.pe_ratio !== null && (
        <div className="mt-3 p-2 bg-gray-50 rounded text-xs">
          <p className="text-gray-600">
            {stock.pe_ratio < 15 && 'This stock may be undervalued based on P/E ratio.'}
            {stock.pe_ratio >= 15 && stock.pe_ratio <= 30 && 'This stock has a moderate P/E ratio.'}
            {stock.pe_ratio > 30 && 'This stock may be overvalued based on P/E ratio.'}
          </p>
        </div>
      )}
    </div>
  );
}