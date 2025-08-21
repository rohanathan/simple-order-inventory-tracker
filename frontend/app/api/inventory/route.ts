import { NextRequest, NextResponse } from 'next/server'

// Mock inventory data for development
// In production, this would fetch from DynamoDB
const mockInventory = [
  {
    sku: 'SKU-RED-001',
    stock: 15,
    reorderThreshold: 5,
    lastUpdatedAt: new Date().toISOString()
  },
  {
    sku: 'SKU-BLU-002',
    stock: 3,
    reorderThreshold: 5,
    lastUpdatedAt: new Date().toISOString()
  },
  {
    sku: 'SKU-GRN-003',
    stock: 8,
    reorderThreshold: 5,
    lastUpdatedAt: new Date().toISOString()
  },
  {
    sku: 'SKU-YLW-004',
    stock: 0,
    reorderThreshold: 5,
    lastUpdatedAt: new Date().toISOString()
  }
]

export async function GET() {
  try {
    // In production, this would fetch from DynamoDB inventory table
    return NextResponse.json({
      success: true,
      inventory: mockInventory
    })

  } catch (error) {
    console.error('Error fetching inventory:', error)
    return NextResponse.json(
      { error: 'Failed to fetch inventory' },
      { status: 500 }
    )
  }
}