# Vercel Quick Start Guide

## 🚀 Deploy in 5 Minutes

### Step 1: Create GitHub Repository
```powershell
cd "c:\Users\User\cursor\Pask-5"

# If Git not installed, download from: https://git-scm.com/download/win
git init
git add .
git commit -m "Network Scanner: Supabase + Vercel integration"
```

### Step 2: Push to GitHub
```powershell
# 1. Create new repo at https://github.com/new (name: "network-scanner")
# 2. Copy the URL (e.g., https://github.com/rimgals/network-scanner.git)

git remote add origin https://github.com/YOUR_USERNAME/network-scanner.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Vercel
1. Visit: https://vercel.com/new
2. Click **"Import Git Repository"**
3. Paste: `https://github.com/YOUR_USERNAME/network-scanner.git`
4. Select **Python** framework
5. Add Environment Variables:
   - `SUPABASE_URL` = `https://mxcjlnezxewqxdrjayor.supabase.co`
   - `SUPABASE_KEY` = `sb_publishable_OfQ4HjEEoeIDGtaYMFOXVg_LJG8uxDp`
6. Click **Deploy** ✨

### Step 4: Access Your App
Once deployed, visit:
- **Dashboard**: `https://your-project.vercel.app/`
- **API Endpoint**: `https://your-project.vercel.app/api/scan`

## 📊 Dashboard Features

- **Scan Control**: Run network scan on-demand
- **Statistics**: View scan count and database size
- **Device List**: Browse all discovered devices
- **Real-time Updates**: Auto-refresh from Supabase

## 🔗 API Endpoint

**GET** `/api/scan` - Scan network and return results

```bash
curl https://your-project.vercel.app/api/scan
```

**Response:**
```json
{
  "success": true,
  "backend": "Supabase",
  "scanned_devices": 9,
  "total_devices": 45,
  "timestamp": "2026-02-06T19:22:16.737673",
  "devices": [...]
}
```

## 🛠️ Troubleshooting

### Import Error
- Ensure `requirements.txt` has `requests>=2.32.0`
- Check Python runtime is `3.9+`

### Timeout Issues
- Vercel free tier: 10 second limit
- Reduce ping packets in `network_scanner.py`
- Upgrade to Pro for 60 second limit

### Supabase Connection Error
- Verify env vars in Vercel dashboard
- Ensure `irenginiai` table exists
- Check API key is valid

## 📁 Project Structure

```
.
├── network_scanner.py      # Core scanner logic
├── api/
│   └── scan.py            # Vercel serverless function
├── public/
│   └── index.html         # Web dashboard
├── vercel.json            # Vercel config
├── requirements.txt       # Python dependencies
└── README.md              # Full documentation
```

## 🔄 CI/CD Workflow

1. Push to GitHub → Auto-triggers Vercel build
2. Vercel installs dependencies from `requirements.txt`
3. Deploys `api/scan.py` as serverless function
4. Serves `public/index.html` as root

**No manual deploy needed!** Every git push auto-deploys.

## 📈 Monitoring

View logs in Vercel dashboard:
1. Go to **Deployments**
2. Click latest deployment
3. Select **Function Logs**
4. Monitor real-time execution

## 🎯 Next Steps

- **Cron Jobs**: Schedule periodic scans (requires Pro)
- **Webhooks**: Trigger external services on scan complete
- **API Keys**: Secure endpoint with authentication
- **Database**: Backup Supabase data regularly

---

**Docs**: See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed setup
