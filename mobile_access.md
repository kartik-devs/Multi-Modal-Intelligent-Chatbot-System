# Mobile Access for Your Chatbot Application

During an interview, you may want to let the interviewer access your chatbot from their mobile device. Here's how to set it up:

## Option 1: Same Network Access

If you and the interviewer are on the same WiFi network:

1. Find your computer's local IP address:
   - Windows: Open Command Prompt and type `ipconfig`
   - Mac: Open Terminal and type `ifconfig`
   - Look for IPv4 Address (usually starts with 192.168.x.x or 10.0.x.x)

2. Run the Flask application:
   ```bash
   python app.py
   ```

3. The interviewer can access your application by entering your IP address followed by the port in their browser:
   ```
   http://YOUR_IP_ADDRESS:5000
   ```
   
   For example: `http://192.168.1.5:5000`

## Option 2: Public Access via ngrok (Recommended)

If you're not on the same network or prefer a simpler solution:

1. [Download ngrok](https://ngrok.com/download) (free)

2. Extract the downloaded file and run it

3. Start a tunnel to your Flask application:
   ```bash
   ngrok http 5000
   ```

4. ngrok will provide a public URL (like `https://abcd1234.ngrok.io`)

5. The interviewer can access your application using this URL from any device

## Before the Interview

1. Test both methods before your interview to make sure they work
2. Have ngrok already installed and ready to go
3. Create a QR code for your ngrok URL to make it even easier for the interviewer to access:
   - Go to a QR code generator site like [QR Code Generator](https://www.qr-code-generator.com/)
   - Enter your ngrok URL
   - Download or display the QR code

## During the Interview

1. Start your Flask application: `python app.py`
2. Start ngrok: `ngrok http 5000`
3. Show the interviewer the ngrok URL or QR code
4. They can scan it with their phone's camera and instantly access your chatbot

This approach demonstrates your ability to deploy and share your application, which is an additional technical skill beyond just coding the application itself. 