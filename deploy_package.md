# Deployment Package for n8n Server

## 📁 **Files to Upload**

Upload these files to your n8n server:

### **1. standalone_scraper.py**
- Main script file
- Upload to: `/path/to/your/n8n/server/`

### **2. standalone_requirements.txt**
- Dependencies file
- Upload to: `/path/to/your/n8n/server/`

### **3. chatbot/ folder**
- Upload the entire `chatbot/` folder
- Should contain: `chatbot/services/playwright_ucr.py`

## 🔧 **Server Setup Commands**

Run these commands on your n8n server:

```bash
# Navigate to your upload directory
cd /path/to/your/n8n/server/

# Install Python dependencies
pip install -r standalone_requirements.txt

# Install Playwright browser
playwright install chromium

# Test the script
python standalone_scraper.py --json '{"line_items":[{"ZipCode":"90001","CPTcode":"99214","date":"2025-04-25"}]}' --acctkey C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs
```

## 🎯 **n8n Execute Command**

In your n8n workflow, use:

```bash
python standalone_scraper.py --json '{"line_items":[{"ZipCode":"90001","CPTcode":"99214","date":"2025-04-25"}]}' --acctkey C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs
```

## ✅ **Advantages**

- ✅ **No HTTP requests** - Direct execution
- ✅ **No authentication** - No tokens needed
- ✅ **Fast execution** - No network overhead
- ✅ **Simple setup** - Just upload and run
- ✅ **Full control** - All code runs on your server

## 🚨 **Requirements**

- Python 3.7+ installed on server
- Internet access for Playwright browser download
- Write permissions in the upload directory
