import { NextRequest, NextResponse } from 'next/server';

interface RouteContext {
  params: {
    symbol: string;
  };
}

export async function GET(request: NextRequest, context: RouteContext) {
  try {
    const symbol = context.params.symbol;
    
    if (!symbol) {
      return NextResponse.json(
        { error: 'Symbol parameter is required' },
        { status: 400 }
      );
    }

    // Get backend URL - use internal Docker network URL when available
    // In some environments, hostname resolution may not work, so we try multiple approaches
    const backendUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // If we're in Docker and hostname doesn't work, try the direct IP
    let url;
    try {
      url = `${backendUrl}/stock-info/${encodeURIComponent(symbol)}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return NextResponse.json(data);
    } catch (error) {
      // If the hostname-based URL fails and we're likely in Docker, try direct backend container IP
      if (backendUrl.includes('backend:8000') && error instanceof Error && error.message.includes('getaddrinfo EAI_AGAIN')) {
        console.log('Backend hostname resolution failed, trying direct IP...');
        try {
          // Try the common Docker bridge network IP for backend
          url = `http://172.18.0.3:8000/stock-info/${encodeURIComponent(symbol)}`;
          const response = await fetch(url, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (!response.ok) {
            const errorText = await response.text();
            console.error('Backend API error:', response.status, errorText);
            return NextResponse.json(
              { error: 'Failed to fetch stock data from backend' },
              { status: response.status }
            );
          }

          const data = await response.json();
          return NextResponse.json(data);
        } catch (fallbackError) {
          console.error('Fallback IP connection also failed:', fallbackError);
        }
      }
      
      console.error('Backend API error:', error);
      return NextResponse.json(
        { error: 'Failed to fetch stock data from backend' },
        { status: 503 }
      );
    }

  } catch (error) {
    console.error('Error proxying stock info request:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}