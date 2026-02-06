# Deploying to Vercel

## Prerequisites

1. **Vercel Account**: https://vercel.com/signup
2. **GitHub Account**: https://github.com (Vercel integrates with GitHub)
3. **Git installed locally**: https://git-scm.com/download/win

## Setup Steps

### 1. Initialize Git Repository

```powershell
cd "c:\Users\User\cursor\Pask-5"
git init
git add .
git commit -m "Initial commit: Network Scanner with Supabase integration"
```

### 2. Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository named `network-scanner` (or your preferred name)
3. Copy the remote URL (e.g., `https://github.com/rimgals/network-scanner.git`)

### 3. Push to GitHub

```powershell
git remote add origin https://github.com/YOUR_USERNAME/network-scanner.git
git branch -M main
git push -u origin main
```

### 4. Deploy to Vercel

**Option A: Via Vercel Dashboard (Recommended)**

1. Go to https://vercel.com/rimgals-projects
2. Click **"New Project"**
3. Select **"Import Git Repository"**
4. Paste your GitHub repository URL
5. Select **Python** as framework
6. Add environment variables:
   - `SUPABASE_URL`: `https://mxcjlnezxewqxdrjayor.supabase.co`
   - `SUPABASE_KEY`: `sb_publishable_OfQ4HjEEoeIDGtaYMFOXVg_LJG8uxDp`
7. Click **"Deploy"**

**Option B: Via Vercel CLI**

```powershell
# Install Vercel CLI
npm install -g vercel

# Deploy from project directory
cd "c:\Users\User\cursor\Pask-5"
vercel

# Add environment variables when prompted
```

## After Deployment

Once deployed, your API will be available at:

```
https://your-project-name.vercel.app/api/scan
```

### Test the API

```powershell
# Using PowerShell
Invoke-WebRequest -Uri "https://your-project-name.vercel.app/api/scan" -Method GET
```

### Response Example

```json
{
  "success": true,
  "backend": "Supabase",
  "scanned_devices": 9,
  "total_devices": 9,
  "timestamp": "2026-02-06T19:22:16.737673",
  "devices": [...]
}
```

## File Structure for Vercel

```
.
├── api/
│   └── scan.py           # Serverless function endpoint
├── network_scanner.py    # Main scanner logic
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
├── README.md            # Documentation
└── .gitignore           # Git ignore rules
```

## Environment Variables (Set in Vercel Dashboard)

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase API key

## Troubleshooting

### Import Error: "ModuleNotFoundError"

If you get import errors, ensure:
1. `requirements.txt` includes all dependencies
2. Python path is correctly set in `api/scan.py`
3. All modules are in the project root

### Supabase Connection Failed

1. Verify environment variables are set in Vercel dashboard
2. Check Supabase credentials are correct
3. Ensure `irenginiai` table exists in Supabase

### Timeout Issues

Network scanning can take time. Vercel's timeout:
- Free tier: 10 seconds
- Pro tier: 60 seconds

For longer scans, consider:
1. Reducing number of ping packets
2. Lowering timeout values
3. Running as background job (requires Pro plan)

## Next Steps

- Monitor logs: Vercel dashboard → Deployments → Function Logs
- Set up webhooks or cron jobs to run scans periodically
- Create a simple frontend dashboard to visualize scan results
