import json
import os

# Read the current GIS scraper
with open('/workspace/scrapers/duval_gis.py', 'r') as f:
    current_content = f.read()

# Create enhanced scraper with actual HTTP requests and HTML parsing
enhanced_scraper = '''#!/usr/bin/env python3
"""
Duval County GIS Property Map Scraper
Source: https://maps.coj.net/duvalproperty/
Portal Type: ArcGIS
"""
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import time

class DuvalGISScraper:
    SOURCE_ID = "duval_gis"
    BASE_URL = "https://maps.coj.net/duvalproperty"
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def _discover_arcgis_services(self) -> List[Dict]:
        """Try to discover ArcGIS REST service endpoints."""
        services = []
        
        try:
            # Try common ArcGIS REST endpoints
            possible_endpoints = [
                f"{self.BASE_URL}/arcgis/rest/services",
                f"{self.BASE_URL}/rest/services",
                "https://maps.coj.net/arcgis/rest/services",
                "https://maps.coj.net/rest/services"
            ]
            
            for endpoint in possible_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=30)
                    if response.status_code == 200:
                        services.append({
                            'endpoint': endpoint,
                            'status': 'accessible',
                            'content_type': response.headers.get('Content-Type', 'unknown')
                        })
                        print(f"Found ArcGIS endpoint: {endpoint}")
                except:
                    continue
        
        except Exception as e:
            print(f"Error discovering ArcGIS services: {e}")
        
        return services
    
    def query_parcels(self, bounds: Optional[Dict] = None) -> List[Dict]:
        """Query parcels from GIS service."""
        parcels = []
        
        try:
            # First, try to discover ArcGIS REST endpoints
            services = self._discover_arcgis_services()
            
            if services:
                # Use the first discovered endpoint
                base_endpoint = services[0]['endpoint']
                
                # Try to query the parcels layer
                # Common layer names: Parcels, Property, RealProperty
                query_url = f"{base_endpoint}/Parcels/MapServer/0/query"
                
                params = {
                    'f': 'json',
                    'where': '1=1',
                    'outFields': '*',
                    'returnGeometry': 'true',
                    'outSR': '4326',  # WGS84
                    'resultRecordCount': 1000
                }
                
                response = self.session.get(query_url, params=params, timeout=60)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if 'features' in data:
                            for feature in data['features']:
                                parcel = {
                                    'source_id': self.SOURCE_ID,
                                    'scraped_at': datetime.now().isoformat(),
                                    'geometry': feature.get('geometry', {}),
                                    'attributes': feature.get('attributes', {})
                                }
                                parcels.append(parcel)
                            
                            print(f"Found {len(parcels)} parcels from ArcGIS REST API")
                    except:
                        # Response might not be JSON
                        print("ArcGIS response was not JSON - may need authentication or different endpoint")
            else:
                print("No ArcGIS REST endpoints discovered - may require authentication or different access method")
        
        except Exception as e:
            print(f"Error querying GIS parcels: {e}")
        
        return parcels
    
    def get_parcel_geometry(self, re_number: str) -> Dict:
        """Get geometry for a specific parcel."""
        geometry = {}
        
        try:
            services = self._discover_arcgis_services()
            
            if services:
                base_endpoint = services[0]['endpoint']
                query_url = f"{base_endpoint}/Parcels/MapServer/0/query"
                
                params = {
                    'f': 'json',
                    'where': f"RE_NUMBER='{re_number}'",
                    'outFields': '*',
                    'returnGeometry': 'true',
                    'outSR': '4326'
                }
                
                response = self.session.get(query_url, params=params, timeout=60)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if 'features' in data and len(data['features']) > 0:
                            feature = data['features'][0]
                            geometry = {
                                're_number': re_number,
                                'source_id': self.SOURCE_ID,
                                'scraped_at': datetime.now().isoformat(),
                                'geometry': feature.get('geometry', {}),
                                'attributes': feature.get('attributes', {})
                            }
                            print(f"Found geometry for RE# {re_number}")
                    except:
                        print("Could not parse ArcGIS geometry response")
        
        except Exception as e:
            print(f"Error getting geometry: {e}")
        
        return geometry
    
    def refresh(self, cursor: Optional[str] = None) -> Dict:
        """Run monthly refresh for GIS data."""
        print("Refreshing GIS data...")
        
        # Discover available services
        services = self._discover_arcgis_services()
        
        # Try to get sample parcels
        parcels = self.query_parcels()
        
        return {
            'source_id': self.SOURCE_ID,
            'records_fetched': len(parcels),
            'new_records': parcels,
            'updated_cursor': datetime.now().strftime('%Y-%m-%d'),
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'services_discovered': len(services),
            'service_endpoints': [s['endpoint'] for s in services]
        }

if __name__ == '__main__':
    config = {'source_url': 'https://maps.coj.net/duvalproperty/'}
    scraper = DuvalGISScraper(config)
    result = scraper.refresh()
    print(json.dumps(result, indent=2))
'''

# Write the enhanced scraper
with open('/workspace/scrapers/duval_gis.py', 'w') as f:
    f.write(enhanced_scraper)

print("Enhanced GIS scraper written successfully")
print(f"File size: {len(enhanced_scraper)} characters")

# Verify it was written correctly
with open('/workspace/scrapers/duval_gis.py', 'r') as f:
    verify = f.read()
    
print(f"Verification - file exists and has {len(verify)} characters")
