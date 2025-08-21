import { NextRequest, NextResponse } from 'next/server'

// For now, we'll use mock data since we don't have AWS credentials configured
// Once deployed to Amplify, replace with actual DynamoDB integration

const mockOrders = [
  {
    orderId: 'ORD-1724155200000-1',
    createdAt: new Date().toISOString(),
    items: [
      { sku: 'SKU-RED-001', qty: 2 },
      { sku: 'SKU-BLU-002', qty: 1 }
    ],
    status: 'RECEIVED'
  }
]

let orderCounter = 2

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { items } = body

    if (!items || !Array.isArray(items) || items.length === 0) {
      return NextResponse.json(
        { error: 'Items array is required and must not be empty' },
        { status: 400 }
      )
    }

    // Validate items
    for (const item of items) {
      if (!item.sku || !item.qty || item.qty <= 0) {
        return NextResponse.json(
          { error: 'Each item must have a valid sku and quantity > 0' },
          { status: 400 }
        )
      }
    }

    const orderId = `ORD-${Date.now()}-${orderCounter++}`
    
    const newOrder = {
      orderId,
      createdAt: new Date().toISOString(),
      items: items.map((item: any) => ({
        sku: item.sku,
        qty: parseInt(item.qty) || 1
      })),
      status: 'RECEIVED'
    }

    // Add to mock data (in production, this would save to DynamoDB)
    mockOrders.unshift(newOrder)

    return NextResponse.json({
      success: true,
      orderId,
      message: 'Order created successfully'
    })

  } catch (error) {
    console.error('Error creating order:', error)
    return NextResponse.json(
      { error: 'Failed to create order' },
      { status: 500 }
    )
  }
}

export async function GET() {
  try {
    // In production, this would fetch from DynamoDB
    return NextResponse.json({
      success: true,
      orders: mockOrders.slice(0, 20) // Return latest 20 orders
    })

  } catch (error) {
    console.error('Error fetching orders:', error)
    return NextResponse.json(
      { error: 'Failed to fetch orders' },
      { status: 500 }
    )
  }
}