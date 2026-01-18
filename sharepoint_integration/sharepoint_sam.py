"""
SAM.gov API to SharePoint Online Integration
Fetches contract opportunities from SAM.gov and syncs to SharePoint list
"""

import os
import time
import json
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from msal import ConfidentialClientApplication
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Config:
    """Application configuration"""
    # SAM.gov API
    sam_api_key: str
    # Azure AD / SharePoint
    tenant_id: str
    client_id: str
    client_secret: str
    sharepoint_site_url: str  # https://tenant.sharepoint.com/sites/sitename
    sharepoint_list_name: str
    sam_api_base_url: str = "https://api.sam.gov/opportunities/v2/search"

    # Sync settings
    days_to_sync: int = 30  # How far back to pull opportunities
    rate_limit_delay: float = 0.11  # SAM.gov: 10 req/sec = 0.1s, use 0.11 for safety


# Set-Aside code mappings
SETASIDE_CODES = {
    "SBA": "Total Small Business Set-Aside (FAR 19.5)",
    "SBP": "Partial Small Business Set-Aside (FAR 19.5)",
    "8A": "8(a) Set-Aside (FAR 19.8)",
    "8AN": "8(a) Sole Source (FAR 19.8)",
    "HZC": "Historically Underutilized Business (HUBZone) Set-Aside (FAR 19.13)",
    "HZS": "Historically Underutilized Business (HUBZone) Sole Source (FAR 19.13)",
    "SDVOSBC": "Service-Disabled Veteran-Owned Small Business (SDVOSB) Set-Aside (FAR 19.14)",
    "SDVOSBS": "Service-Disabled Veteran-Owned Small Business (SDVOSB) Sole Source (FAR 19.14)",
    "WOSB": "Women-Owned Small Business (WOSB) Program Set-Aside (FAR 19.15)",
    "WOSBSS": "Women-Owned Small Business (WOSB) Program Sole Source (FAR 19.15)",
    "EDWOSB": "Economically Disadvantaged WOSB (EDWOSB) Program Set-Aside (FAR 19.15)",
    "EDWOSBSS": "Economically Disadvantaged WOSB (EDWOSB) Program Sole Source (FAR 19.15)",
    "LAS": "Local Area Set-Aside (FAR 26.2)",
    "IEE": "Indian Economic Enterprise (IEE) Set-Aside",
    "ISBEE": "Indian Small Business Economic Enterprise (ISBEE) Set-Aside",
    "BICiv": "Buy Indian Set-Aside",
    "VSA": "Veteran-Owned Small Business Set-Aside",
    "VSS": "Veteran-Owned Small Business Sole source"
}


# ============================================================================
# SAM.GOV API CLIENT
# ============================================================================

class SAMGovClient:
    """Handles SAM.gov API requests"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
    
    def search_opportunities(
        self,
        posted_from: str,
        posted_to: str,
        limit: int = 5,
        offset: int = 0
    ) -> Dict:
        """
        Search for opportunities in SAM.gov
        
        Args:
            posted_from: Date in format MM/DD/YYYY
            posted_to: Date in format MM/DD/YYYY
            limit: Max results per page (max 100)
            offset: Pagination offset
        """
        params = {
            "api_key": self.config.sam_api_key,
            "postedFrom": posted_from,
            "postedTo": posted_to,
            "limit": limit,
            "offset": offset
        }
        
        logger.info(f"Fetching opportunities: offset={offset}, limit={limit}")
        
        try:
            response = self.session.get(
                self.config.sam_api_base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # Rate limiting
            time.sleep(self.config.rate_limit_delay)
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"SAM.gov API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error fetching opportunities: {str(e)}")
            raise
    
    def fetch_all_opportunities(self, days_back: int = 30) -> List[Dict]:
        """
        Fetch all opportunities from the last N days
        Handles pagination automatically
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        posted_from = start_date.strftime("%m/%d/%Y")
        posted_to = end_date.strftime("%m/%d/%Y")
        
        logger.info(f"Fetching opportunities from {posted_from} to {posted_to}")
        
        all_opportunities = []
        offset = 0
        limit = 10
        
        while True:
            data = self.search_opportunities(posted_from, posted_to, limit, offset)
            
            opportunities = data.get("opportunitiesData", [])
            all_opportunities.extend(opportunities)
            
            total_records = data.get("totalRecords", 0)
            logger.info(f"Fetched {len(all_opportunities)} of {total_records} opportunities")
            
            # Check if we've fetched all records
            if len(all_opportunities) >= total_records:
                break
            
            offset += limit
        
        logger.info(f"Total opportunities fetched: {len(all_opportunities)}")
        return all_opportunities
    
    def download_file(self, url: str, filename: str) -> bytes:
        """Download a file from SAM.gov resource link"""
        try:
            # Add API key to URL
            url_with_key = f"{url}?api_key={self.config.sam_api_key}"
            
            response = self.session.get(url_with_key, timeout=60)
            response.raise_for_status()
            
            time.sleep(self.config.rate_limit_delay)
            
            logger.info(f"Downloaded file: {filename}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error downloading {filename}: {str(e)}")
            return None


# ============================================================================
# SHAREPOINT CLIENT
# ============================================================================

class SharePointClient:
    """Handles SharePoint authentication and operations"""
    
    def __init__(self, config: Config):
        self.config = config
        self.access_token = None
        self.site_id = None
        self.list_id = None
        self.sharepoint_hostname = None
        self.site_relative_url = None
        self._parse_site_url()
    
    def _parse_site_url(self):
        """Parse SharePoint site URL into components"""
        # Example: https://tenant.sharepoint.com/sites/sitename
        parts = self.config.sharepoint_site_url.replace("https://", "").split("/")
        self.sharepoint_hostname = parts[0]
        if len(parts) > 1:
            self.site_relative_url = "/" + "/".join(parts[1:])
        else:
            self.site_relative_url = ""
    
    def authenticate(self):
        """Acquire access token using client credentials"""
        authority = f"https://login.microsoftonline.com/{self.config.tenant_id}"
        app = ConfidentialClientApplication(
            self.config.client_id,
            authority=authority,
            client_credential=self.config.client_secret,
        )
        
        # Get token for Graph API
        result = app.acquire_token_for_client(
            scopes=["https://graph.microsoft.com/.default"]
        )
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            logger.info("✓ Graph API authentication successful")
        else:
            raise Exception(f"Authentication failed: {result.get('error_description')}")
        
        # Also get token for SharePoint REST API (for attachments)
        sp_result = app.acquire_token_for_client(
            scopes=[f"https://{self.sharepoint_hostname}/.default"]
        )
        
        if "access_token" in sp_result:
            self.sp_rest_token = sp_result["access_token"]
            logger.info("✓ SharePoint REST API authentication successful")
        else:
            raise Exception(f"SP REST auth failed: {sp_result.get('error_description')}")
    
    def _graph_headers(self) -> Dict[str, str]:
        """Headers for Graph API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _sp_rest_headers(self) -> Dict[str, str]:
        """Headers for SharePoint REST API requests"""
        return {
            "Authorization": f"Bearer {self.sp_rest_token}",
            "Accept": "application/json;odata=verbose"
        }
    
    def get_site_id(self) -> str:
        """Get SharePoint site ID via Graph API"""
        if self.site_id:
            return self.site_id
        
        url = f"https://graph.microsoft.com/v1.0/sites/{self.sharepoint_hostname}:{self.site_relative_url}"
        response = requests.get(url, headers=self._graph_headers())
        response.raise_for_status()
        
        self.site_id = response.json()["id"]
        logger.info(f"✓ Site ID: {self.site_id}")
        return self.site_id
    
    def get_list_id(self) -> str:
        """Get SharePoint list ID"""
        if self.list_id:
            return self.list_id
        
        site_id = self.get_site_id()
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists"
        response = requests.get(url, headers=self._graph_headers())
        response.raise_for_status()
        
        lists = response.json().get("value", [])
        for lst in lists:
            if lst["displayName"] == self.config.sharepoint_list_name:
                self.list_id = lst["id"]
                logger.info(f"✓ List ID: {self.list_id}")
                return self.list_id
        
        raise Exception(f"List '{self.config.sharepoint_list_name}' not found")
    
    def get_existing_notice_ids(self) -> set:
        """Get all existing NoticeId values from SharePoint"""
        site_id = self.get_site_id()
        list_id = self.get_list_id()
        
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items?$expand=fields&$select=fields"
        
        existing_ids = set()
        
        while url:
            response = requests.get(url, headers=self._graph_headers())
            response.raise_for_status()
            data = response.json()
            
            for item in data.get("value", []):
                notice_id = item.get("fields", {}).get("NoticeId")
                if notice_id:
                    existing_ids.add(notice_id)
            
            url = data.get("@odata.nextLink")
        
        logger.info(f"Found {len(existing_ids)} existing opportunities in SharePoint")
        return existing_ids
    
    def create_list_item(self, fields: Dict) -> Dict:
        """Create a new list item via Graph API"""
        site_id = self.get_site_id()
        list_id = self.get_list_id()
        
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items"
        payload = {"fields": fields}
        
        response = requests.post(url, headers=self._graph_headers(), json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def add_attachment_rest(self, item_id: str, filename: str, file_content: bytes) -> bool:
        """
        Add attachment to list item using SharePoint REST API
        Graph API does not support list item attachments, must use REST API
        """
        # SharePoint REST endpoint for adding attachments
        url = (
            f"https://{self.sharepoint_hostname}{self.site_relative_url}/"
            f"_api/web/lists/getbytitle('{self.config.sharepoint_list_name}')/"
            f"items({item_id})/AttachmentFiles/add(FileName='{filename}')"
        )
        
        headers = {
            "Authorization": f"Bearer {self.sp_rest_token}",
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/octet-stream"
        }
        
        try:
            response = requests.post(url, headers=headers, data=file_content)
            response.raise_for_status()
            logger.info(f"✓ Attached file: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to attach {filename}: {str(e)}")
            return False


# ============================================================================
# DATA TRANSFORMATION
# ============================================================================

class OpportunityTransformer:
    """Transforms SAM.gov opportunity data to SharePoint format"""
    
    @staticmethod
    def parse_department_info(full_path: str) -> tuple:
        """
        Parse fullParentPathName into components
        Example: "STATE, DEPARTMENT OF.STATE, DEPARTMENT OF.US EMBASSY BOGOTA"
        Returns: (department, subtier, office)
        """
        if not full_path:
            return (None, None, None)
        
        parts = full_path.split(".")
        
        department = parts[0] if len(parts) > 0 else None
        subtier = parts[1] if len(parts) > 1 else None
        office = parts[2] if len(parts) > 2 else None
        
        return (department, subtier, office)
    
    @staticmethod
    def format_date(date_str: str) -> Optional[str]:
        """Convert date string to ISO format for SharePoint"""
        if not date_str:
            return None
        
        try:
            # SAM.gov returns dates like "2025-12-31" or "2026-01-26T16:00:00-05:00"
            if "T" in date_str:
                # Already ISO format
                return date_str
            else:
                # Add time component
                return f"{date_str}T00:00:00Z"
        except:
            return None
    
    @staticmethod
    def get_poc_info(poc_list: List[Dict]) -> Dict:
        """Extract primary point of contact information"""
        if not poc_list:
            return {}
        
        # Find primary contact
        primary = next((p for p in poc_list if p.get("type") == "primary"), poc_list[0])
        
        return {
            "POC_Name": primary.get("fullName"),
            "POC_Email": primary.get("email"),
            "POC_Phone": primary.get("phone"),
            "POC_Title": primary.get("title")
        }
    
    @staticmethod
    def get_place_of_performance(pop: Dict) -> Dict:
        """Extract place of performance information"""
        if not pop:
            return {}
        
        city = pop.get("city", {})
        state = pop.get("state", {})
        country = pop.get("country", {})
        
        return {
            "PoP_City": city.get("name") if isinstance(city, dict) else None,
            "PoP_State": state.get("name") if isinstance(state, dict) else None,
            "PoP_Country": country.get("name") if isinstance(country, dict) else None
        }
    
    @staticmethod
    def get_award_info(award: Dict) -> Dict:
        """Extract award information if available"""
        if not award:
            return {}
        
        awardee = award.get("awardee", {})
        
        return {
            "AwardNumber": award.get("number"),
            "AwardAmount": award.get("amount"),
            "AwardDate": OpportunityTransformer.format_date(award.get("date")),
            "AwardeeName": awardee.get("name") if isinstance(awardee, dict) else None,
            "AwardeeLocation": awardee.get("location") if isinstance(awardee, dict) else None
        }
    
    @staticmethod
    def transform(opp: Dict) -> Dict:
        """Transform SAM.gov opportunity to SharePoint fields"""
        department, subtier, office = OpportunityTransformer.parse_department_info(
            opp.get("fullParentPathName")
        )
        
        # Get set-aside description
        set_aside_code = opp.get("typeOfSetAside")
        set_aside_desc = SETASIDE_CODES.get(set_aside_code, set_aside_code) if set_aside_code else None
        
        # Build base fields
        fields = {
            "Title": opp.get("title"),
            "NoticeId": opp.get("noticeId"),
            "SolicitationNumber": opp.get("solicitationNumber"),
            "Department": department,
            "Subtier": subtier,
            "Office": office,
            "FullParentPath": opp.get("fullParentPathName"),
            "FullParentCode": opp.get("fullParentPathCode"),
            "PostedDate": OpportunityTransformer.format_date(opp.get("postedDate")),
            "ResponseDeadline": OpportunityTransformer.format_date(opp.get("responseDeadLine")),
            "Type": opp.get("type"),
            "BaseType": opp.get("baseType"),
            "SetAsideCode": set_aside_code,
            "SetAsideDescription": set_aside_desc,
            "NAICSCode": opp.get("naicsCode"),
            "ClassificationCode": opp.get("classificationCode"),
            "Active": opp.get("active"),
            "OrganizationType": opp.get("organizationType"),
            "AdditionalInfoLink": opp.get("additionalInfoLink"),
            "UILink": opp.get("uiLink"),
            "DescriptionLink": opp.get("description")
        }
        
        # Add POC info
        poc_info = OpportunityTransformer.get_poc_info(opp.get("pointOfContact", []))
        fields.update(poc_info)
        
        # Add place of performance
        pop_info = OpportunityTransformer.get_place_of_performance(opp.get("placeOfPerformance"))
        fields.update(pop_info)
        
        # Add award info if available
        award_info = OpportunityTransformer.get_award_info(opp.get("award"))
        fields.update(award_info)
        
        # Remove None values
        fields = {k: v for k, v in fields.items() if v is not None}
        
        return fields


# ============================================================================
# MAIN SYNC ORCHESTRATOR
# ============================================================================

class SyncOrchestrator:
    """Orchestrates the sync between SAM.gov and SharePoint"""
    
    def __init__(self, config: Config):
        self.config = config
        self.sam_client = SAMGovClient(config)
        self.sp_client = SharePointClient(config)
    
    def sync(self, download_attachments: bool = True):
        """Run the sync process"""
        logger.info("=== Starting SAM.gov to SharePoint Sync ===")
        
        # Authenticate
        self.sp_client.authenticate()
        
        # Get existing opportunities
        existing_ids = self.sp_client.get_existing_notice_ids()
        
        # Fetch opportunities from SAM.gov
        opportunities = self.sam_client.fetch_all_opportunities(
            days_back=self.config.days_to_sync
        )
        
        # Process each opportunity
        new_count = 0
        skipped_count = 0
        error_count = 0
        
        for opp in opportunities:
            notice_id = opp.get("noticeId")
            
            # Skip if already exists
            if notice_id in existing_ids:
                skipped_count += 1
                logger.debug(f"Skipping existing: {notice_id}")
                continue
            
            try:
                # Transform data
                fields = OpportunityTransformer.transform(opp)
                
                # Create list item
                item = self.sp_client.create_list_item(fields)
                item_id = item["id"]
                logger.info(f"✓ Created: {opp.get('title')[:50]}... (ID: {item_id})")
                
                # Download and attach files
                if download_attachments:
                    resource_links = opp.get("resourceLinks", [])
                    for idx, link in enumerate(resource_links):
                        filename = f"{notice_id}_attachment_{idx+1}.pdf"
                        file_content = self.sam_client.download_file(link, filename)
                        
                        if file_content:
                            self.sp_client.add_attachment_rest(item_id, filename, file_content)
                
                new_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing {notice_id}: {str(e)}")
        
        # Summary
        logger.info("=== Sync Complete ===")
        logger.info(f"New opportunities created: {new_count}")
        logger.info(f"Skipped (already exists): {skipped_count}")
        logger.info(f"Errors: {error_count}")
        logger.info(f"Total processed: {len(opportunities)}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main execution function"""
    
    # Load configuration from environment variables
    config = Config(
        sam_api_key=os.getenv("SAM_API_KEY"),
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        client_id=os.getenv("AZURE_CLIENT_ID"),
        client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        sharepoint_site_url=os.getenv("SHAREPOINT_SITE_URL"),
        sharepoint_list_name=os.getenv("SHAREPOINT_LIST_NAME", "SAM Opportunities"),
        days_to_sync=int(os.getenv("DAYS_TO_SYNC", "30"))
    )
    
    # Validate required config
    required_fields = [
        config.sam_api_key,
        config.tenant_id,
        config.client_id,
        config.client_secret,
        config.sharepoint_site_url
    ]
    
    if not all(required_fields):
        raise ValueError("Missing required configuration. Check environment variables.")
    
    # Run sync
    orchestrator = SyncOrchestrator(config)
    orchestrator.sync(download_attachments=True)

# if __name__ == "__main__":
#     main()