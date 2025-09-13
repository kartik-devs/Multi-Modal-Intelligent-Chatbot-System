# Standalone UCR Scraper - No Backend Required!

## 🎯 **Perfect for n8n Integration**

You're absolutely right! You don't need to host the full Flask backend. The standalone script is much simpler and perfect for n8n integration.

## 🚀 **Quick Setup**

### **1. Install Dependencies**
```bash
pip install -r standalone_requirements.txt
playwright install chromium
```

### **2. Usage Options**

#### **Option A: From JSON File**
```bash
python standalone_scraper.py --file input.json --acctkey C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs
```

#### **Option B: From JSON String**
```bash
python standalone_scraper.py --json '{"line_items":[{"ZipCode":"90001","CPTcode":"99214","date":"2025-04-25"}]}' --acctkey C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs
```

#### **Option C: From stdin (Perfect for n8n)**
```bash
echo '{"line_items":[{"ZipCode":"90001","CPTcode":"99214","date":"2025-04-25"}]}' | python standalone_scraper.py --acctkey C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs
```

## 🔧 **n8n Integration**

### **Method 1: Execute Command Node**
1. Add **Execute Command** node in n8n
2. Configure:
   - **Command**: `python`
   - **Arguments**: `standalone_scraper.py --acctkey C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs`
   - **Input**: JSON data from previous node

### **Method 2: Code Node + Execute Command**
```javascript
// In n8n Code node - prepare the command
const jsonData = {
  line_items: $input.all().map(item => ({
    ZipCode: item.json.zip_code,
    CPTcode: item.json.cpt_code,
    date: item.json.service_date
  }))
};

return [{
  json: {
    command: "python",
    args: ["standalone_scraper.py", "--acctkey", "C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs"],
    input: JSON.stringify(jsonData)
  }
}];
```

## 📊 **Input/Output Examples**

### **Input JSON**
```json
{
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
    }
  ]
}
```

### **Output JSON**
```json
{
  "results": [
    {
      "procedureCode": "99214",
      "percentiles": {
        "50": 272.56,
        "55": 285.02,
        "60": 295.09,
        "65": 304.6,
        "70": 319.22,
        "75": 362.4,
        "80": 389.13,
        "85": 435.52,
        "90": 517.42,
        "95": 776.66
      },
      "currency": "USD",
      "zip_code": 90001,
      "date": "04/25/2025",
      "line_number": 1
    }
  ],
  "total_processed": 2,
  "successful": 2,
  "failed": 0
}
```

## 🎯 **Advantages of Standalone Approach**

### ✅ **Pros**
- **No server required** - Just run the script
- **No authentication** - No JWT tokens needed
- **Lightweight** - Only the scraper code
- **Fast startup** - No Flask overhead
- **Easy deployment** - Just copy the script
- **Perfect for n8n** - Execute Command node works great

### ❌ **Cons**
- **No concurrent requests** - One process at a time
- **No persistent storage** - Results only in output
- **No web interface** - Command line only

## 🔄 **n8n Workflow Examples**

### **Simple Workflow**
```
[Trigger] → [Execute Command] → [Process Results]
```

### **With Data Transformation**
```
[Trigger] → [Code Transform] → [Execute Command] → [Process Results]
```

### **Batch Processing**
```
[Trigger] → [Split Items] → [Execute Command] → [Merge Results]
```

## 🚀 **Deployment Options**

### **Option 1: Local Machine**
- Run n8n and scraper on same machine
- Use local file paths

### **Option 2: Docker Container**
```dockerfile
FROM python:3.9-slim
COPY standalone_scraper.py /app/
COPY chatbot/ /app/chatbot/
WORKDIR /app
RUN pip install -r standalone_requirements.txt
RUN playwright install chromium
CMD ["python", "standalone_scraper.py"]
```

### **Option 3: Cloud Function**
- Deploy as AWS Lambda, Google Cloud Function, etc.
- Trigger via n8n webhook

## 📝 **Command Line Options**

```bash
python standalone_scraper.py --help
```

**Available options:**
- `--json`: JSON input as string
- `--file`: JSON input file path  
- `--acctkey`: UCR account key (required)
- `--output`: Output file path (optional)

## 🎉 **Ready to Use!**

The standalone scraper is:
- ✅ **Tested and working**
- ✅ **n8n compatible**
- ✅ **No backend required**
- ✅ **Simple to deploy**
- ✅ **Perfect for automation**

Just use the **Execute Command** node in n8n with the standalone script!
