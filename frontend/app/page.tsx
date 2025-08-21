'use client'

import { useState, useEffect } from 'react'

interface InventoryItem {
  sku: string
  stock: number
}

interface OrderItem {
  sku: string
  qty: number
}

export default function OrderPage() {
  const [inventory, setInventory] = useState<InventoryItem[]>([])
  const [orderItems, setOrderItems] = useState<OrderItem[]>([{ sku: '', qty: 1 }])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchInventory()
  }, [])

  const fetchInventory = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_GATEWAY_URL}/inventory`, {
        method: 'GET',
      })
      const result = await response.json()
      setInventory(result.inventory || [])
    } catch (error) {
      console.error('Failed to fetch inventory:', error)
    }
  }

  const addOrderItem = () => {
    setOrderItems([...orderItems, { sku: '', qty: 1 }])
  }

  const removeOrderItem = (index: number) => {
    if (orderItems.length > 1) {
      setOrderItems(orderItems.filter((_, i) => i !== index))
    }
  }

  const updateOrderItem = (index: number, field: keyof OrderItem, value: string | number) => {
    const updated = [...orderItems]
    updated[index] = { ...updated[index], [field]: value }
    setOrderItems(updated)
  }

  const placeOrder = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage('')

    const validItems = orderItems.filter(item => item.sku && item.qty > 0)
    
    if (validItems.length === 0) {
      setMessage('Please add at least one valid item')
      setLoading(false)
      return
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_GATEWAY_URL}/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ items: validItems }),
      })

      const result = await response.json()

      if (response.ok) {
        setMessage(`Order placed successfully! Order ID: ${result.orderId}`)
        setOrderItems([{ sku: '', qty: 1 }])
        fetchInventory() // Refresh inventory
      } else {
        setMessage(`Error: ${result.error}`)
      }
    } catch (error) {
      setMessage('Failed to place order. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">Place Order</h1>
        
        {/* Available Inventory */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Available Products</h2>
          {inventory.length > 0 ? (
            <div className="grid grid-cols-2 gap-4">
              {inventory.map((item) => (
                <div key={item.sku} className="border rounded p-3">
                  <div className="font-medium">{item.sku}</div>
                  <div className={`text-sm ${item.stock > 0 ? 'text-green-600' : 'text-red-600'}`}>
                    Stock: {item.stock}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500">Loading inventory...</div>
          )}
        </div>

        {/* Order Form */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Create Order</h2>
          
          {message && (
            <div className={`mb-4 p-3 rounded ${
              message.includes('successfully') 
                ? 'bg-green-100 text-green-700' 
                : 'bg-red-100 text-red-700'
            }`}>
              {message}
            </div>
          )}

          <form onSubmit={placeOrder}>
            <div className="space-y-4">
              {orderItems.map((item, index) => (
                <div key={index} className="flex gap-4 items-end">
                  <div className="flex-1">
                    <label className="block text-sm font-medium mb-1">Product SKU</label>
                    <select
                      value={item.sku}
                      onChange={(e) => updateOrderItem(index, 'sku', e.target.value)}
                      className="w-full border border-gray-300 rounded px-3 py-2"
                      required
                    >
                      <option value="">Select product</option>
                      {inventory.map((product) => (
                        <option 
                          key={product.sku} 
                          value={product.sku}
                          disabled={product.stock === 0}
                        >
                          {product.sku} (Stock: {product.stock})
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="w-24">
                    <label className="block text-sm font-medium mb-1">Qty</label>
                    <input
                      type="number"
                      min="1"
                      value={item.qty}
                      onChange={(e) => updateOrderItem(index, 'qty', parseInt(e.target.value) || 1)}
                      className="w-full border border-gray-300 rounded px-3 py-2"
                      required
                    />
                  </div>
                  
                  <button
                    type="button"
                    onClick={() => removeOrderItem(index)}
                    disabled={orderItems.length === 1}
                    className="bg-red-500 hover:bg-red-600 disabled:bg-gray-300 text-white px-3 py-2 rounded"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>

            <div className="mt-6 flex gap-4">
              <button
                type="button"
                onClick={addOrderItem}
                className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
              >
                Add Item
              </button>
              
              <button
                type="submit"
                disabled={loading}
                className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-2 rounded"
              >
                {loading ? 'Placing Order...' : 'Place Order'}
              </button>
            </div>
          </form>
        </div>
      </div>

      <style jsx global>{`
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
        .min-h-screen { min-height: 100vh; }
        .bg-gray-50 { background-color: #f9fafb; }
        .bg-white { background-color: white; }
        .shadow { box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .rounded-lg { border-radius: 0.5rem; }
        .rounded { border-radius: 0.25rem; }
        .max-w-2xl { max-width: 42rem; }
        .mx-auto { margin: 0 auto; }
        .px-4 { padding: 0 1rem; }
        .py-8 { padding: 2rem 0; }
        .p-6 { padding: 1.5rem; }
        .p-3 { padding: 0.75rem; }
        .mb-8 { margin-bottom: 2rem; }
        .mb-6 { margin-bottom: 1.5rem; }
        .mb-4 { margin-bottom: 1rem; }
        .mb-1 { margin-bottom: 0.25rem; }
        .mt-6 { margin-top: 1.5rem; }
        .text-3xl { font-size: 1.875rem; }
        .text-xl { font-size: 1.25rem; }
        .text-sm { font-size: 0.875rem; }
        .font-bold { font-weight: 700; }
        .font-semibold { font-weight: 600; }
        .font-medium { font-weight: 500; }
        .text-center { text-align: center; }
        .grid { display: grid; }
        .grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
        .gap-4 { gap: 1rem; }
        .space-y-4 > * + * { margin-top: 1rem; }
        .flex { display: flex; }
        .items-end { align-items: flex-end; }
        .flex-1 { flex: 1; }
        .w-full { width: 100%; }
        .w-24 { width: 6rem; }
        .border { border: 1px solid #d1d5db; }
        .border-gray-300 { border-color: #d1d5db; }
        .px-3 { padding: 0 0.75rem; }
        .py-2 { padding: 0.5rem 0; }
        .px-6 { padding: 0 1.5rem; }
        .px-4 { padding: 0 1rem; }
        .block { display: block; }
        .bg-blue-500 { background-color: #3b82f6; }
        .hover\\:bg-blue-600:hover { background-color: #2563eb; }
        .bg-gray-500 { background-color: #6b7280; }
        .hover\\:bg-gray-600:hover { background-color: #4b5563; }
        .bg-red-500 { background-color: #ef4444; }
        .hover\\:bg-red-600:hover { background-color: #dc2626; }
        .disabled\\:bg-gray-300:disabled { background-color: #d1d5db; }
        .disabled\\:bg-gray-400:disabled { background-color: #9ca3af; }
        .text-white { color: white; }
        .text-green-600 { color: #16a34a; }
        .text-red-600 { color: #dc2626; }
        .text-gray-500 { color: #6b7280; }
        .bg-green-100 { background-color: #dcfce7; }
        .text-green-700 { color: #15803d; }
        .bg-red-100 { background-color: #fee2e2; }
        .text-red-700 { color: #b91c1c; }
      `}</style>
    </div>
  )
}