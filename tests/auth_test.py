from sharepoint_integration.sharepoint_sam import Config, SharePointClient
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
