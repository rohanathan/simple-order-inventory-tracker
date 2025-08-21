# Simple Order Management System

A minimal order processing system with DynamoDB, Lambda functions, and Next.js frontend. Place orders through a web interface and automatically update inventory with email alerts for low stock.

## Architecture

```
Next.js Frontend → API Gateway → Lambda Functions → DynamoDB
                                       ↓
                                 DynamoDB Streams
                                       ↓
                              Inventory Update Lambda
                                       ↓
                                 SNS Email Alerts
```

## 🚀 Features

- **Simple Order Form**: One-page interface to place orders
- **Real-time Inventory Display**: Shows available products and stock levels
- **Automatic Inventory Updates**: Stock decreases automatically when orders are placed
- **Low Stock Email Alerts**: Get notified when inventory runs low
- **Serverless**: Built with AWS Lambda, DynamoDB, and Amplify

## Project Structure

```
├── README.md
├── frontend/                    # Next.js application
│   ├── app/
│   │   ├── page.tsx            # Main order form page
│   │   ├── layout.tsx          # App layout
│   │   └── api/                # Mock API routes for development
│   ├── package.json
│   ├── amplify.yml             # Amplify build configuration
│   └── .env.local              # Environment variables
├── backend/                    # AWS Lambda functions
│   ├── lambda/
│   │   ├── inventory_check.py  # Inventory validation & alerts
│   │   └── index_to_opensearch.py  # OpenSearch integration (future)
│   └── scripts/
│       └── seed_orders.py      # Sample data generator
└── aws-inventory-orders-mvp/   # Original MVP files
```

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript
- **Backend**: AWS Lambda (Python 3.11)
- **Database**: DynamoDB with Streams
- **Notifications**: Amazon SNS/SES
- **Hosting**: AWS Amplify
- **API**: AWS API Gateway

##  Data Models

### Orders Table (DynamoDB)
```json
{
  "orderId": "ORD-123",
  "createdAt": "2025-08-20T15:00:00Z",
  "items": [
    {
      "sku": "SKU-RED-001",
      "qty": 2
    }
  ],
  "status": "RECEIVED"
}
```

### Inventory Table (DynamoDB)
```json
{
  "sku": "SKU-RED-001",
  "stock": 12,
  "reorderThreshold": 5,
  "lastUpdatedAt": "2025-08-20T15:01:00Z"
}
```

## Quick Start

### Prerequisites
- AWS Account with CLI configured
- Node.js 18+ installed
- GitHub account

### 1. Backend Setup (AWS Console)

#### Create DynamoDB Tables
1. **Orders Table**:
   - Table name: `orders`
   - Partition key: `orderId` (String)
   - Enable DynamoDB Streams with "New image"

2. **Inventory Table**:
   - Table name: `inventory`
   - Partition key: `sku` (String)

#### Create SNS Topic
1. Create topic: `low-stock-alerts`
2. Subscribe your email and confirm subscription

#### Deploy Lambda Functions
1. Upload `backend/lambda/inventory_check.py` as Lambda function
2. Set environment variables:
   ```
   ORDERS_TABLE=orders
   INVENTORY_TABLE=inventory
   SNS_TOPIC_ARN=<your-sns-topic-arn>
   ```
3. Connect DynamoDB Stream as trigger

#### Create API Gateway
1. Create REST API with two resources:
   - `GET /inventory` → `get_inventory_lambda`
   - `POST /orders` → `place_order_lambda`
2. Enable CORS for frontend integration
3. Deploy to stage (e.g., `dev`)

### 2. Frontend Deployment

#### Local Testing
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000`

#### Deploy to AWS Amplify
1. Push code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. In AWS Amplify Console:
   - Connect to GitHub repository
   - Build settings auto-detected from `amplify.yml`
   - Add environment variable:
     ```
     NEXT_PUBLIC_API_GATEWAY_URL=https://your-api-gateway-url/dev
     ```

### 3. Seed Sample Data
```bash
cd backend/scripts
python seed_orders.py --region us-east-1 --orders 5
```

## Testing

### Test Order Flow
1. Visit your Amplify app URL
2. Select products from available inventory
3. Place an order
4. Check inventory updates in real-time
5. Verify email alerts for low stock items

### Verify Backend
- **DynamoDB**: Check orders and inventory tables for data
- **CloudWatch**: Review Lambda function logs
- **SNS**: Confirm email delivery for low stock alerts

## Current API Endpoints

Replace `<your-api-gateway-url>` with your actual API Gateway URL:

- **GET** `/inventory` - Fetch current inventory levels
- **POST** `/orders` - Place a new order

Example order payload:
```json
{
  "items": [
    {
      "sku": "SKU-RED-001",
      "qty": 2
    }
  ]
}
```

## Future Enhancements

- [ ] OpenSearch integration for data visualization
- [ ] Order history and tracking
- [ ] User authentication
- [ ] Product management interface
- [ ] Advanced inventory analytics
- [ ] Mobile app support

## 🔧 Configuration

### Environment Variables

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_GATEWAY_URL=https://your-api-gateway-url/dev
```

**Lambda Functions**
```
ORDERS_TABLE=orders
INVENTORY_TABLE=inventory
SNS_TOPIC_ARN=arn:aws:sns:region:account:low-stock-alerts
```

## Troubleshooting

### Common Issues

**Orders not processing**
- Check DynamoDB Streams are enabled on orders table
- Verify Lambda function has correct IAM permissions
- Review CloudWatch logs for errors

**Email alerts not working**
- Confirm SNS subscription is confirmed
- Check Lambda environment variables
- Verify SNS topic permissions

**Frontend not connecting to API**
- Ensure CORS is enabled on API Gateway
- Check environment variable `NEXT_PUBLIC_API_GATEWAY_URL`
- Verify API Gateway endpoints are deployed

## Support

- Check CloudWatch logs for detailed error messages
- Verify IAM permissions for all services
- Test individual Lambda functions in AWS Console

## License

MIT License - feel free to use and modify for your projects.