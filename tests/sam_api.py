from sharepoint_integration.sharepoint_sam import SAMGovClient, Config
import os

config = Config(
    sam_api_key=os.getenv("SAM_API_KEY"),
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET"),
    sharepoint_site_url=os.getenv("SHAREPOINT_SITE_URL"),
    sharepoint_list_name=os.getenv("SHAREPOINT_LIST_NAME")
)
sam_client = SAMGovClient(config)
opportunities = sam_client.fetch_all_opportunities(days_back=1)

print(f"Found {len(opportunities)} opportunities from last 24 hours")
if opportunities:
    print(f"Sample: {opportunities}")