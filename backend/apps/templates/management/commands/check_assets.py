from django.core.management.base import BaseCommand
from apps.templates.models import Template
from apps.templates.services.asset_helper import asset_helper
import requests
from urllib.parse import urljoin
from django.conf import settings

class Command(BaseCommand):
    help = 'Проверяет доступность ассетов'
    
    def handle(self, *args, **options):
        templates = Template.objects.filter(is_public=True)
        self.stdout.write(f"Found {templates.count()} public templates")
        
        for template in templates:
            self.stdout.write(self.style.NOTICE(f"\nChecking template: {template.name} (ID: {template.id})"))
            assets = template.assets.all()
            self.stdout.write(f"Template has {assets.count()} assets")
            
            for asset in assets:
                page_text = f"Page {asset.page.index}" if asset.page else "Global asset"
                self.stdout.write(self.style.SUCCESS(f"\n  Asset: {asset.name} ({page_text})"))
                self.stdout.write(f"  Original URL: {asset.file}")
                
                # Get the URL through asset_helper
                url = asset_helper.get_asset_url(
                    str(template.id),
                    asset.name,
                    str(asset.page.id) if asset.page else None
                )
                
                self.stdout.write(self.style.WARNING(f"  Helper URL: {url}"))
                
                # Try to access the asset
                if url.startswith('/'):
                    # Local URL, need to add base
                    test_url = f"http://localhost{url}"
                else:
                    test_url = url
                
                self.stdout.write(f"  Testing URL: {test_url}")
                
                try:
                    # Disable SSL verification for local testing
                    response = requests.head(test_url, verify=False, timeout=5)
                    status = response.status_code
                    
                    if status == 200:
                        self.stdout.write(self.style.SUCCESS(f"  Status: {status} OK"))
                    else:
                        self.stdout.write(self.style.ERROR(f"  Status: {status} ERROR"))
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error: {str(e)}"))
                
        self.stdout.write(self.style.SUCCESS("\nAsset check completed")) 