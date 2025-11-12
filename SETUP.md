# Quick Setup Guide

## Step 1: Get Your Claude API Key

1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new API key
5. Copy the key (it starts with `sk-ant-...`)

## Step 2: Configure Your Environment

**Windows:**
```powershell
# Create .env file
echo CLAUDE_API_KEY=your_actual_api_key_here > .env

# Or set as environment variable (PowerShell)
$env:CLAUDE_API_KEY="your_actual_api_key_here"

# Or set permanently (Command Prompt as Administrator)
setx CLAUDE_API_KEY "your_actual_api_key_here"
```

**Mac/Linux:**
```bash
# Create .env file
echo "CLAUDE_API_KEY=your_actual_api_key_here" > .env

# Or add to your shell profile (~/.bashrc or ~/.zshrc)
echo 'export CLAUDE_API_KEY="your_actual_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

**Docker:**
```bash
# Just create the .env file
echo "CLAUDE_API_KEY=your_actual_api_key_here" > .env

# Docker Compose will automatically load it
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Run the Application

The database will initialize automatically on first run!

**Option A: Direct Python**
```bash
python app.py
```

**Option B: Docker**
```bash
docker-compose up -d
```

## Step 5: Test the API

```bash
python test_api.py
```

## Troubleshooting

### "CLAUDE_API_KEY environment variable is not set"
- Make sure you created the `.env` file in the project root
- Or set the environment variable in your terminal
- Restart your terminal/IDE after setting environment variables

### "Authentication error" or "Invalid API key"
- Verify your API key is correct
- Check if the key is active in the Anthropic console
- Make sure there are no extra spaces or quotes in the `.env` file

### Database not found
- The app will automatically create it on first run
- If you see errors, try deleting `tickets.db` and restarting

## What's Next?

1. Visit `http://localhost:5000/api/health` to check if the server is running
2. Check the full API documentation in `README.md`
3. Run the test suite with `python test_api.py`
4. Create your first ticket!

```bash
curl -X POST http://localhost:5000/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Ticket",
    "description": "This is a test ticket to verify the system works",
    "user_name": "Your Name",
    "user_email": "your.email@example.com"
  }'
```

## Need Help?

- See the full README.md for detailed documentation
- Check the troubleshooting section
- Review the API documentation
