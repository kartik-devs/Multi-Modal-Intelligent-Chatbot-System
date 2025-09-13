# n8n Integration Guide for UCR Fee Scraper

## 🚀 **API Endpoint for n8n Integration**

### **Endpoint Details**
- **URL**: `http://localhost:5000/api/scrape/batch-json`
- **Method**: `POST`
- **Authentication**: JWT Bearer Token (required)

### **Headers**
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer YOUR_JWT_TOKEN"
}
```

### **Request Payload**
```json
{
  "acctkey": "C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs",
  "line_items": [
    {
      "ZipCode": "90001",
      "CPTcode": "99214", 
      "date": "2025-04-25"
    },
    {
      "ZipCode": "90001",
      "CPTcode": "20999",
      "date": "2025-04-25"
    },
    {
      "ZipCode": "90001",
      "CPTcode": "92507",
      "date": "2025-04-25"
    }
  ]
}
```

### **Response Format**
```json
{
  "results": [
    {
      "procedureCode": "99214",
      "percentiles": {
        "50": 272.56,
        "55": 285.02,
        "60": 301.38,
        "65": 311.21,
        "70": 330.28,
        "75": 362.4,
        "80": 401.29,
        "85": 444.02,
        "90": 513.64,
        "95": 779.81
      },
      "currency": "USD",
      "zip_code": 90001,
      "date": "04/25/2025",
      "line_number": 1
    }
  ],
  "total_processed": 3,
  "successful": 2,
  "failed": 1
}
```

## 🔧 **n8n Workflow Setup**

### **Step 1: HTTP Request Node**
1. Add an **HTTP Request** node
2. Configure:
   - **Method**: POST
   - **URL**: `http://localhost:5000/api/scrape/batch-json`
   - **Headers**: 
     ```json
     {
       "Content-Type": "application/json",
       "Authorization": "Bearer YOUR_JWT_TOKEN"
     }
     ```
   - **Body**: JSON payload with your data

### **Step 2: Authentication Setup**
To get a JWT token, you can:
1. Use the existing login endpoint: `POST /api/auth/login`
2. Or create a dedicated service account token

### **Step 3: Data Transformation (Optional)**
If your n8n data is in a different format, use a **Code** node to transform it:

```javascript
// Transform n8n data to scraper format
const transformedData = {
  acctkey: "C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs",
  line_items: $input.all().map(item => ({
    ZipCode: item.json.zip_code,
    CPTcode: item.json.cpt_code,
    date: item.json.service_date
  }))
};

return [{ json: transformedData }];
```

## 📊 **Example n8n Workflows**

### **Workflow 1: Simple Batch Processing**
```
[Trigger] → [HTTP Request] → [Process Results]
```

### **Workflow 2: With Data Transformation**
```
[Trigger] → [Code Transform] → [HTTP Request] → [Process Results]
```

### **Workflow 3: Error Handling**
```
[Trigger] → [HTTP Request] → [IF Error] → [Send Alert] → [Continue]
```

## 🔐 **Authentication Options**

### **Option 1: JWT Token (Recommended)**
```bash
# Get token via login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### **Option 2: Service Account (Future Enhancement)**
We can create a dedicated service account for n8n integration.

## 📝 **Input Data Formats**

### **Supported Date Formats**
- `YYYY-MM-DD` (e.g., "2025-04-25") ✅
- `MM/DD/YYYY` (e.g., "04/25/2025") ✅

### **Required Fields**
- `ZipCode`: 5-digit ZIP code
- `CPTcode`: CPT/HCPCS procedure code
- `date`: Service date

### **Optional Fields**
- `acctkey`: Can be provided per request or set globally

## 🚨 **Error Handling**

### **Common Errors**
- `400`: Missing required fields
- `401`: Invalid or missing JWT token
- `500`: Server error during processing

### **Response Error Format**
```json
{
  "error": "Error description",
  "results": [
    {
      "error": "Specific error for this line item",
      "line_number": 1
    }
  ]
}
```

## 🔄 **Processing Status**

The API returns processing statistics:
- `total_processed`: Total number of line items
- `successful`: Number of successful lookups
- `failed`: Number of failed lookups

## 🎯 **Best Practices for n8n**

1. **Batch Size**: Process 10-50 items per request for optimal performance
2. **Rate Limiting**: Add delays between requests if processing large datasets
3. **Error Handling**: Always check the `failed` count in the response
4. **Data Validation**: Validate input data before sending to the API
5. **Logging**: Log responses for debugging and monitoring

## 🚀 **Quick Start Example**

```bash
# Test the endpoint
curl -X POST http://localhost:5000/api/scrape/batch-json \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "acctkey": "C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs",
    "line_items": [
      {
        "ZipCode": "90001",
        "CPTcode": "99214",
        "date": "2025-04-25"
      }
    ]
  }'
```

This setup allows n8n to easily integrate with your UCR fee scraper for automated batch processing!
