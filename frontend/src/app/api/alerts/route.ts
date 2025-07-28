import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Validate the request body
    if (!body.stockName || !body.keywords) {
      return NextResponse.json(
        { message: 'Stock name and keywords are required' },
        { status: 400 }
      )
    }

    // Simulate API processing delay
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Log the alert data (in a real app, this would be saved to database)
    console.log('New alert created:', {
      stockName: body.stockName,
      keywords: body.keywords,
      timestamp: new Date().toISOString()
    })

    // Return success response
    return NextResponse.json({
      message: 'Alert created successfully',
      alert: {
        id: Date.now().toString(),
        stockName: body.stockName,
        keywords: body.keywords,
        created: new Date().toISOString()
      }
    })

  } catch (error) {
    console.error('Error creating alert:', error)
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    )
  }
}