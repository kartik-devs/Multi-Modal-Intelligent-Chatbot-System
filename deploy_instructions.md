# Deploying Your Chatbot to Render

This guide will walk you through deploying your Multi-Modal Intelligent Chatbot to Render, giving you a permanent URL that works on mobile devices and is perfect for interviews.

## Step 0: Make Your GitHub Repository Private

Since your code contains an API key, it's crucial to keep your repository private:

1. Go to your GitHub repository
2. Click on "Settings" (tab near the top right)
3. Scroll down to the "Danger Zone" section
4. Click "Change repository visibility"
5. Select "Make private"
6. Type your repository name to confirm
7. Click "I understand, make this repository private"

## Step 1: Sign up for Render

1. Go to [render.com](https://render.com/) and sign up for a free account
2. Verify your email address

## Step 2: Connect Your GitHub Repository

1. In your Render dashboard, click "New +"
2. Select "Web Service"
3. Choose "Build and deploy from a Git repository"
4. Connect your GitHub account if you haven't already
5. Select your private repository

## Step 3: Configure Your Web Service

You can use the automatic configuration from the `render.yaml` file, or configure manually:

### Manual Configuration:
- **Name**: chatbot (or any name you prefer)
- **Environment**: Python
- **Region**: Choose the closest to your location
- **Branch**: main (or your default branch)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Instance Type**: Free (or paid if you need more resources)

## Step 4: Set Up Environment Variables (Optional but Recommended)

For better security, you can store your API key as an environment variable:

1. In your Render dashboard, go to your web service
2. Click on the "Environment" tab
3. Add a new environment variable:
   - Key: `GROQ_API_KEY`
   - Value: Your Groq API key
4. Click "Save Changes"

This keeps your API key out of your code repository entirely.

## Step 5: Deploy Your Application

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Wait for the deployment to complete (5-10 minutes)
4. Once deployed, Render will provide a URL like `https://chatbot-xxxx.onrender.com`

## Step 6: Generate a QR Code for Interviews

1. Go to a QR code generator site like [QR Code Generator](https://www.qr-code-generator.com/)
2. Enter your Render URL
3. Download the QR code image
4. During interviews, show this QR code to let interviewers access your application

## Advantages of Using Render

- **Permanent URL**: Unlike ngrok, your Render URL doesn't expire
- **Professional Appearance**: Shows you understand deployment
- **Free Tier**: No cost for basic usage
- **No Local Dependencies**: Runs in the cloud, no need for local Ollama
- **Secure**: Can store sensitive API keys as environment variables

## Important Notes

1. **Free Tier Limitations**:
   - Your app may "sleep" after 15 minutes of inactivity
   - When someone accesses it, it will "wake up" (takes 30-60 seconds)
   - For interviews, visit the URL before the interview to wake it up

2. **Ollama Not Available**:
   - The app is configured to use Groq API by default on Render
   - Ollama option will show an appropriate message if selected

3. **Updating Your Application**:
   - Push changes to your GitHub repository
   - Render will automatically redeploy

4. **Custom Domain (Optional)**:
   - You can add a custom domain in Render settings for a more professional URL 