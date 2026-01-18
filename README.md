# SharePoint List Schema for SAM.gov Opportunities

## List Creation

1. Navigate to your SharePoint site
2. Click **New** → **List**
3. Name it: **SAM Opportunities** (or your preferred name)
4. Create the following columns:

---

## Required Columns

### Core Identification

| Column Name | Type | Required | Indexed | Notes |
|-------------|------|----------|---------|-------|
| **Title** | Single line of text | Yes | No | Default column - Opportunity title |
| **NoticeId** | Single line of text | Yes | **Yes** | Unique ID from SAM.gov - MUST BE INDEXED |
| **SolicitationNumber** | Single line of text | No | Yes | For searching/filtering |

**Important**: Index the `NoticeId` column for performance:
- Column Settings → Advanced → Set as indexed

---

### Department/Agency Information

| Column Name | Type | Required | Notes |
|-------------|------|----------|-------|
| **Department** | Single line of text | No | Top-level agency (e.g., "STATE, DEPARTMENT OF") |
| **Subtier** | Single line of text | No | Sub-agency |
| **Office** | Single line of text | No | Specific office |
| **FullParentPath** | Multiple lines of text | No | Complete hierarchy path |
| **FullParentCode** | Single line of text | No | Agency code |

---

### Dates and Timeline

| Column Name | Type | Required | Format | Notes |
|-------------|------|----------|--------|-------|
| **PostedDate** | Date and Time | No | Include time | When opportunity was posted |
| **ResponseDeadline** | Date and Time | No | Include time | Submission deadline |

---

### Opportunity Classification

| Column Name | Type | Required | Choices/Notes |
|-------------|------|----------|---------------|
| **Type** | Choice | No | See choices below |
| **BaseType** | Single line of text | No | Base type classification |
| **Active** | Choice | No | Choices: Yes, No |
| **OrganizationType** | Single line of text | No | e.g., "OFFICE" |

**Type Column Choices**:
- Combined Synopsis/Solicitation
- Presolicitation
- Solicitation
- Sources Sought
- Special Notice
- Intent to Bundle Requirements (DoD-Funded)
- Sale of Surplus Property
- Justification and Approval

---

### Set-Aside Information

| Column Name | Type | Required | Choices |
|-------------|------|----------|---------|
| **SetAsideCode** | Choice | No | See Set-Aside codes below |
| **SetAsideDescription** | Multiple lines of text | No | Full description |

**SetAsideCode Column Choices**:
- SBA - Total Small Business Set-Aside
- SBP - Partial Small Business Set-Aside
- 8A - 8(a) Set-Aside
- 8AN - 8(a) Sole Source
- HZC - HUBZone Set-Aside
- HZS - HUBZone Sole Source
- SDVOSBC - SDVOSB Set-Aside
- SDVOSBS - SDVOSB Sole Source
- WOSB - Women-Owned Small Business Set-Aside
- WOSBSS - Women-Owned Small Business Sole Source
- EDWOSB - Economically Disadvantaged WOSB Set-Aside
- EDWOSBSS - Economically Disadvantaged WOSB Sole Source
- LAS - Local Area Set-Aside
- IEE - Indian Economic Enterprise Set-Aside
- ISBEE - Indian Small Business Economic Enterprise Set-Aside
- BICiv - Buy Indian Set-Aside
- VSA - Veteran-Owned Small Business Set-Aside
- VSS - Veteran-Owned Small Business Sole Source

---

### Industry Codes

| Column Name | Type | Required | Notes |
|-------------|------|----------|-------|
| **NAICSCode** | Single line of text | No | Primary NAICS code |
| **ClassificationCode** | Single line of text | No | PSC/FSC code |

---

### Point of Contact

| Column Name | Type | Required | Notes |
|-------------|------|----------|-------|
| **POC_Name** | Single line of text | No | Full name |
| **POC_Email** | Single line of text | No | Email address |
| **POC_Phone** | Single line of text | No | Phone number |
| **POC_Title** | Single line of text | No | Job title |

---

### Place of Performance

| Column Name | Type | Required | Notes |
|-------------|------|----------|-------|
| **PoP_City** | Single line of text | No | City name |
| **PoP_State** | Single line of text | No | State name |
| **PoP_Country** | Single line of text | No | Country name |

---

### Links and Resources

| Column Name | Type | Required | Notes |
|-------------|------|----------|-------|
| **UILink** | Hyperlink | No | Link to SAM.gov opportunity page |
| **AdditionalInfoLink** | Hyperlink | No | Additional information URL |
| **DescriptionLink** | Hyperlink | No | Link to description endpoint |

---

### Award Information (Optional - for awarded contracts)

| Column Name | Type | Required | Notes |
|-------------|------|----------|-------|
| **AwardNumber** | Single line of text | No | Contract award number |
| **AwardAmount** | Currency | No | Award value |
| **AwardDate** | Date and Time | No | Date awarded |
| **AwardeeName** | Single line of text | No | Name of awardee |
| **AwardeeLocation** | Single line of text | No | Awardee location |

---

## Default Columns (Keep These)

| Column Name | Notes |
|-------------|-------|
| **Attachments** | System column - used for PDF attachments |
| **Created** | System column - auto-populated |
| **Created By** | System column - auto-populated |
| **Modified** | System column - auto-populated |
| **Modified By** | System column - auto-populated |

---

## Recommended Views

### 1. Active Opportunities (Default View)
**Columns to show**:
- Title
- SolicitationNumber
- Department
- ResponseDeadline
- SetAsideCode
- Active

**Filter**: Active equals "Yes"  
**Sort**: ResponseDeadline (ascending)

---

### 2. Recent Posts
**Columns to show**:
- Title
- SolicitationNumber
- Department
- PostedDate
- Type

**Filter**: PostedDate is greater than [Today]-30  
**Sort**: PostedDate (descending)

---

### 3. By Set-Aside Type
**Columns to show**:
- Title
- SolicitationNumber
- SetAsideDescription
- ResponseDeadline
- Department

**Group By**: SetAsideCode  
**Sort**: ResponseDeadline (ascending)

---

## Column Creation Quick Reference

### To Create a Single Line of Text Column:
1. Click **+ Add column** → **Single line of text**
2. Enter column name
3. Click **Save**

### To Create a Choice Column:
1. Click **+ Add column** → **Choice**
2. Enter column name
3. Add choices (one per line)
4. Set default value (optional)
5. Click **Save**

### To Create a Date Column:
1. Click **+ Add column** → **Date and time**
2. Enter column name
3. Select **Include time**
4. Click **Save**

### To Create a Currency Column:
1. Click **+ Add column** → **Number**
2. Enter column name (e.g., AwardAmount)
3. Format: **Currency**
4. Decimal places: 2
5. Min/Max: Leave blank
6. Click **Save**

### To Create a Hyperlink Column:
1. Click **+ Add column** → **Hyperlink**
2. Enter column name
3. Click **Save**

---

## PowerShell Script to Create All Columns

```powershell
# Connect to SharePoint Online
Connect-PnPOnline -Url "https://yourtenant.sharepoint.com/sites/yoursite" -Interactive

$listName = "SAM Opportunities"

# Single line text columns
$textColumns = @(
    "NoticeId",
    "SolicitationNumber",
    "Department",
    "Subtier",
    "Office",
    "FullParentCode",
    "BaseType",
    "OrganizationType",
    "ClassificationCode",
    "NAICSCode",
    "POC_Name",
    "POC_Email",
    "POC_Phone",
    "POC_Title",
    "PoP_City",
    "PoP_State",
    "PoP_Country",
    "AwardNumber",
    "AwardeeName",
    "AwardeeLocation"
)

foreach ($col in $textColumns) {
    Add-PnPField -List $listName -DisplayName $col -InternalName $col -Type Text
}

# Multi-line text columns
Add-PnPField -List $listName -DisplayName "FullParentPath" -InternalName "FullParentPath" -Type Note
Add-PnPField -List $listName -DisplayName "SetAsideDescription" -InternalName "SetAsideDescription" -Type Note

# Date columns
Add-PnPField -List $listName -DisplayName "PostedDate" -InternalName "PostedDate" -Type DateTime -AddToDefaultView
Add-PnPField -List $listName -DisplayName "ResponseDeadline" -InternalName "ResponseDeadline" -Type DateTime -AddToDefaultView
Add-PnPField -List $listName -DisplayName "AwardDate" -InternalName "AwardDate" -Type DateTime

# Currency
Add-PnPField -List $listName -DisplayName "AwardAmount" -InternalName "AwardAmount" -Type Currency

# URL/Hyperlink columns
Add-PnPField -List $listName -DisplayName "UILink" -InternalName "UILink" -Type URL
Add-PnPField -List $listName -DisplayName "AdditionalInfoLink" -InternalName "AdditionalInfoLink" -Type URL
Add-PnPField -List $listName -DisplayName "DescriptionLink" -InternalName "DescriptionLink" -Type URL

# Choice columns
$typeChoices = @(
    "Combined Synopsis/Solicitation",
    "Presolicitation",
    "Solicitation",
    "Sources Sought",
    "Special Notice",
    "Intent to Bundle Requirements",
    "Sale of Surplus Property",
    "Justification and Approval"
)
Add-PnPField -List $listName -DisplayName "Type" -InternalName "Type" -Type Choice -Choices $typeChoices

Add-PnPField -List $listName -DisplayName "Active" -InternalName "Active" -Type Choice -Choices @("Yes", "No")

$setAsideChoices = @("SBA", "SBP", "8A", "8AN", "HZC", "HZS", "SDVOSBC", "SDVOSBS", "WOSB", "WOSBSS", "EDWOSB", "EDWOSBSS", "LAS", "IEE", "ISBEE", "BICiv", "VSA", "VSS")
Add-PnPField -List $listName -DisplayName "SetAsideCode" -InternalName "SetAsideCode" -Type Choice -Choices $setAsideChoices

# Index the NoticeId column
Set-PnPField -List $listName -Identity "NoticeId" -Values @{Indexed=$true}

Write-Host "✓ All columns created successfully!"
```

---

## Testing Your Schema

After creating the list, test by manually adding one row with sample data:

```
Title: "Test Opportunity"
NoticeId: "test123"
SolicitationNumber: "TEST-2025-001"
Department: "TEST DEPARTMENT"
PostedDate: Today
ResponseDeadline: Tomorrow
Active: "Yes"
```

Then verify the Python script can read it:
```python
existing_ids = sp_client.get_existing_notice_ids()
print(existing_ids)  # Should show: {'test123'}
```

---

## Important Notes

1. **NoticeId MUST be indexed** - This is critical for performance
2. **Choice columns** - Make sure spelling matches exactly (case-sensitive)
3. **Attachments** - Don't create this column manually; it's automatic
4. **Column internal names** - Use the exact names shown in the code
5. **Required columns** - Only Title is required to allow script to create items

---

## Permissions Needed

Your Azure AD app needs these SharePoint permissions:
- **Sites.ReadWrite.All** (to read/write list items)
- **Sites.FullControl.All** (if using REST API for attachments)

Grant these in Azure Portal → App Registration → API Permissions


# SAM.gov to SharePoint - Setup & Deployment Guide

## Prerequisites

### 1. Python Dependencies

```bash
pip install msal requests python-dotenv
```

### 2. SAM.gov API Access

**Get your free API key:**
1. Go to https://sam.gov/data-services/
2. Click **"Request a Public API Key"**
3. Fill out the form (takes 2-3 minutes)
4. API key will be emailed to you immediately
5. Save the API key - you'll need it later

**Test your API key:**
```bash
curl "https://api.sam.gov/opportunities/v2/search?limit=1&api_key=YOUR_KEY_HERE&postedFrom=01/01/2025&postedTo=01/31/2025"
```

---

## Azure AD Setup

### Step 1: Create App Registration

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
   - **Name**: `SAM.gov SharePoint Integration`
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: Leave blank
4. Click **Register**

### Step 2: Note Your IDs

After creation, you'll see:
- **Application (client) ID** - Copy this
- **Directory (tenant) ID** - Copy this

### Step 3: Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
   - **Description**: `SAM Integration Secret`
   - **Expires**: 24 months (or your preferred duration)
3. Click **Add**
4. **IMMEDIATELY copy the secret value** - you can't see it again!

### Step 4: Grant Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Select **Microsoft Graph**
4. Click **Application permissions**
5. Search for and add:
   - `Sites.ReadWrite.All`
   - `Sites.FullControl.All`
6. Click **Add permissions**
7. Click **Add a permission** again
8. Select **APIs my organization uses**
9. Search for **SharePoint**
10. Click **Application permissions**
11. Add: `Sites.FullControl.All`
12. **Click "Grant admin consent for [Your Organization]"** (requires admin)
13. Verify all permissions show green checkmarks

---

## SharePoint Setup

### Step 1: Create the List

1. Navigate to your SharePoint site
2. Click **New** → **List**
3. Name it: `SAM Opportunities`
4. Follow the [SharePoint List Schema](sharepoint_schema.md) to create all columns

**Quick creation via PowerShell:**
```powershell
# See SharePoint Schema artifact for the full PowerShell script
```

### Step 2: Verify List Creation

Test that you can access the list:
1. Open the list in SharePoint
2. Manually add one test item
3. Verify all columns are visible

---

## Configuration

### Option 1: Environment Variables (Development)

Create a `.env` file in your project directory:

```bash
# SAM.gov API
SAM_API_KEY=your-sam-gov-api-key-here

# Azure AD
AZURE_TENANT_ID=your-tenant-id-here
AZURE_CLIENT_ID=your-client-id-here
AZURE_CLIENT_SECRET=your-client-secret-here

# SharePoint
SHAREPOINT_SITE_URL=https://yourtenant.sharepoint.com/sites/yoursite
SHAREPOINT_LIST_NAME=SAM Opportunities

# Sync Settings (optional)
DAYS_TO_SYNC=30
```

**Load in Python:**
```python
from dotenv import load_dotenv
load_dotenv()

# Your script will automatically read these
```

### Option 2: Azure Key Vault (Production)

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
vault_url = "https://your-keyvault.vault.azure.net/"
client = SecretClient(vault_url=vault_url, credential=credential)

config = Config(
    sam_api_key=client.get_secret("SAM-API-KEY").value,
    tenant_id=client.get_secret("AZURE-TENANT-ID").value,
    client_id=client.get_secret("AZURE-CLIENT-ID").value,
    client_secret=client.get_secret("AZURE-CLIENT-SECRET").value,
    sharepoint_site_url=client.get_secret("SHAREPOINT-SITE-URL").value,
    sharepoint_list_name=client.get_secret("SHAREPOINT-LIST-NAME").value
)
```

---

## Testing

### Test 1: Authentication

```python
from sam_gov_integration import Config, SharePointClient
import os

config = Config(
    sam_api_key=os.getenv("SAM_API_KEY"),
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET"),
    sharepoint_site_url=os.getenv("SHAREPOINT_SITE_URL"),
    sharepoint_list_name=os.getenv("SHAREPOINT_LIST_NAME")
)

sp_client = SharePointClient(config)
sp_client.authenticate()

print("✓ Authentication successful!")
print(f"Site ID: {sp_client.get_site_id()}")
print(f"List ID: {sp_client.get_list_id()}")
```

### Test 2: SAM.gov API

```python
from sam_gov_integration import SAMGovClient

sam_client = SAMGovClient(config)
opportunities = sam_client.fetch_all_opportunities(days_back=1)

print(f"Found {len(opportunities)} opportunities from last 24 hours")
if opportunities:
    print(f"Sample: {opportunities[0].get('title')}")
```

### Test 3: Full Sync (Small Batch)

```python
# Modify the config temporarily
config.days_to_sync = 1  # Only sync last 24 hours

from sam_gov_integration import SyncOrchestrator

orchestrator = SyncOrchestrator(config)
orchestrator.sync(download_attachments=True)
```

---

## Scheduling

### Option 1: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Run daily at 2 AM
0 2 * * * cd /path/to/project && /usr/bin/python3 sam_gov_integration.py >> /var/log/sam_sync.log 2>&1

# Run every 6 hours
0 */6 * * * cd /path/to/project && /usr/bin/python3 sam_gov_integration.py >> /var/log/sam_sync.log 2>&1
```

### Option 2: Windows Task Scheduler

1. Open **Task Scheduler**
2. Click **Create Basic Task**
3. Name: `SAM.gov SharePoint Sync`
4. Trigger: **Daily** (or your preferred schedule)
5. Action: **Start a program**
   - Program: `C:\Python\python.exe`
   - Arguments: `C:\path\to\sam_gov_integration.py`
   - Start in: `C:\path\to\project`
6. Finish

### Option 3: Azure Functions (Recommended)

**Create Function App:**
1. Go to Azure Portal
2. Create a new **Function App**
3. Runtime: **Python 3.10+**
4. Plan: **Consumption** (pay per execution)

**function_app.py:**
```python
import azure.functions as func
import logging
from sam_gov_integration import main, Config
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

app = func.FunctionApp()

@app.timer_trigger(
    schedule="0 0 */6 * * *",  # Every 6 hours
    arg_name="myTimer",
    run_on_startup=False
)
def sam_sync_timer(myTimer: func.TimerRequest) -> None:
    logging.info('SAM.gov sync started')
    
    try:
        main()
        logging.info('SAM.gov sync completed successfully')
    except Exception as e:
        logging.error(f'SAM.gov sync failed: {str(e)}')
        raise
```

**Deploy:**
```bash
func azure functionapp publish your-function-app-name
```

### Option 4: GitHub Actions (Free)

**.github/workflows/sam-sync.yml:**
```yaml
name: SAM.gov Sync

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install msal requests
      
      - name: Run sync
        env:
          SAM_API_KEY: ${{ secrets.SAM_API_KEY }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
          SHAREPOINT_SITE_URL: ${{ secrets.SHAREPOINT_SITE_URL }}
          SHAREPOINT_LIST_NAME: ${{ secrets.SHAREPOINT_LIST_NAME }}
        run: python sam_gov_integration.py
```

Add secrets in GitHub:
- Repository → Settings → Secrets and variables → Actions

---

## Monitoring & Logging

### Basic Logging (File)

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'sam_sync.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[handler, logging.StreamHandler()]
)
```

### Azure Application Insights (Production)

```python
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=your-key-here'
))
```

### Email Alerts on Failure

```python
import smtplib
from email.message import EmailMessage

def send_error_email(error_message):
    msg = EmailMessage()
    msg['Subject'] = 'SAM.gov Sync Failed'
    msg['From'] = 'alerts@yourdomain.com'
    msg['To'] = 'admin@yourdomain.com'
    msg.set_content(f'Sync failed with error:\n\n{error_message}')
    
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('your-email', 'your-password')
        smtp.send_message(msg)

# In your main function:
try:
    orchestrator.sync()
except Exception as e:
    send_error_email(str(e))
    raise
```

---

## Troubleshooting

### Issue: "Authentication failed - AADSTS7000215"

**Cause**: Client secret expired or incorrect

**Fix**:
1. Go to Azure Portal → App registrations → Your app
2. Certificates & secrets
3. Create a new client secret
4. Update your environment variable

---

### Issue: "List 'SAM Opportunities' not found"

**Cause**: List name doesn't match exactly

**Fix**:
```python
# Check what lists exist
response = requests.get(
    f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists",
    headers=headers
)
print([lst['displayName'] for lst in response.json()['value']])
```

Update your config with the exact name (case-sensitive).

---

### Issue: "Access is denied" when adding attachments

**Cause**: Missing SharePoint permissions or wrong authentication scope

**Fix**:
1. Verify `Sites.FullControl.All` permission is granted for SharePoint (not just Graph)
2. Make sure admin consent was granted
3. Wait 5-10 minutes for permissions to propagate

---

### Issue: Rate limit errors from SAM.gov

**Cause**: Exceeding 10 requests/second

**Fix**: The script has built-in rate limiting. If still seeing errors:
```python
config.rate_limit_delay = 0.15  # Increase from 0.11 to 0.15
```
---

### Issue: Files download but are corrupt

**Cause**: SAM.gov resource links require authentication

**Fix**: The script already adds the API key to download URLs. If still failing:
```python
# Check the URL structure
print(f"Downloading from: {url}?api_key={api_key[:10]}...")
```

---

### Issue: "Too many requests" from SharePoint

**Cause**: Creating items too quickly

**Fix**: Add throttling:
```python
import time

for opp in opportunities:
    # ... create item ...
    time.sleep(0.5)  # 500ms delay between creates
```

---

## Best Practices

### 1. Start Small
- First sync: Use `days_to_sync=1` (last 24 hours only)
- Verify data looks correct
- Then increase to 30 days

### 2. Monitor Initially
- Run manually for first few days
- Check SharePoint list after each run
- Review logs for errors

### 3. Handle Failures Gracefully
- The script skips duplicates automatically
- Failed items log errors but don't stop the sync
- Re-running is safe (won't create duplicates)

### 4. Backup Your Data
- Export SharePoint list to Excel weekly
- Store logs for at least 30 days

### 5. Update Filters (Optional)

Only sync specific agencies:
```python
# In SAMGovClient.search_opportunities()
params["deptname"] = "Department of Defense"
```

Only sync certain NAICS codes:
```python
params["ncode"] = "541330"  # Engineering services
```

See SAM.gov API docs for all filter options.

---

## Performance Optimization

### Batch Processing

For very large syncs (1000+ opportunities):
```python
def sync_in_batches(self, batch_size=100):
    opportunities = self.sam_client.fetch_all_opportunities(
        days_back=self.config.days_to_sync
    )
    
    for i in range(0, len(opportunities), batch_size):
        batch = opportunities[i:i + batch_size]
        for opp in batch:
            # Process opportunity
            pass
        
        logger.info(f"Completed batch {i//batch_size + 1}")
        time.sleep(5)  # Rest between batches
```

### Parallel Downloads (Advanced)

```python
from concurrent.futures import ThreadPoolExecutor

def download_attachments_parallel(self, item_id, resource_links):
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for idx, link in enumerate(resource_links):
            filename = f"attachment_{idx+1}.pdf"
            future = executor.submit(
                self.sam_client.download_file,
                link,
                filename
            )
            futures.append((future, filename))
        
        for future, filename in futures:
            content = future.result()
            if content:
                self.sp_client.add_attachment_rest(item_id, filename, content)
```

---

## Next Steps

1. ✅ Complete Azure AD setup
2. ✅ Create SharePoint list with all columns
3. ✅ Get SAM.gov API key
4. ✅ Configure environment variables
5. ✅ Test authentication
6. ✅ Run small test sync (1 day)
7. ✅ Verify data in SharePoint
8. ✅ Set up scheduling
9. ✅ Configure monitoring/alerts
10. ✅ Run full production sync

---

## Support Resources

- **SAM.gov API Docs**: https://open.gsa.gov/api/get-opportunities-public-api/
- **Microsoft Graph Docs**: https://learn.microsoft.com/en-us/graph/
- **SharePoint REST API**: https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/
- **MSAL Python**: https://github.com/AzureAD/microsoft-authentication-library-for-python

---
