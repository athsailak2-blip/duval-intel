# Scheduled Refresh Setup

## Windows (Task Scheduler)

### Option 1: Import XML
1. Open Task Scheduler
2. Click "Import Task" and select `scripts/duval-intel-refresh.xml`
3. Update the working directory path to your actual installation path
4. Set your user credentials
5. Enable the task

### Option 2: Command Line
```powershell
schtasks /create /xml scripts/duval-intel-refresh.xml /tn "Duval-Intel-Refresh" /ru YOUR_USERNAME
```

### Option 3: Manual Setup
1. Open Task Scheduler
2. Create Basic Task
3. Name: "Duval County Intel Refresh"
4. Trigger: Daily at 6:00 AM
5. Action: Start a program
6. Program: `scripts/run_refresh.bat`

## Linux/Mac (Cron)

1. Edit crontab:
```bash
crontab -e
```

2. Add the lines from `scripts/crontab.txt` (adjust paths)

3. Save and exit

## GitHub Actions (Already Configured)

The `.github/workflows/deploy.yml` already includes:
- Daily scheduled run at 11:00 UTC (6:00 AM EST)
- Automatic deployment after refresh

## Manual Refresh

To run a manual refresh:
```bash
# Windows
scripts/run_refresh.bat

# Linux/Mac
scripts/run_refresh.sh

# Python directly
python scripts/daily_refresh.py
```

## Logs

All refresh logs are stored in `logs/refresh.log`
