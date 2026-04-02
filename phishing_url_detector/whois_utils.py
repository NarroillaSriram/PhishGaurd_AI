import whois
import datetime
from urllib.parse import urlparse

def get_domain_info(url):
    """
    Retrieves WHOIS information for a given URL to determine domain age and risk.
    """
    try:
        domain = urlparse(url).netloc
        if not domain:
            domain = urlparse(url).path.split('/')[0] # Handle cases without scheme

        # Remove www.
        if domain.startswith("www."):
            domain = domain[4:]
            
        w = whois.whois(domain)
        
        # Creation Date handling (can be a list or string)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if not creation_date:
            return {
                "domain": domain,
                "creation_date": "Unknown",
                "days_alive": -1,
                "registrar": w.registrar or "Unknown",
                "risk": "Unknown"
            }
            
        # Calculate Age
        today = datetime.datetime.now()
        age = today - creation_date
        days_alive = age.days
        
        # Determine Risk
        # < 30 days = CRITICAL
        # < 6 months = HIGH
        # < 1 year = MEDIUM
        # > 1 year = LOW
        
        risk = "LOW"
        if days_alive < 30:
            risk = "CRITICAL (New Domain)"
        elif days_alive < 180:
            risk = "HIGH (Recent Domain)"
        elif days_alive < 365:
            risk = "MEDIUM"
            
        return {
            "domain": domain,
            "creation_date": creation_date.strftime('%Y-%m-%d'),
            "days_alive": days_alive,
            "registrar": w.registrar or "Unknown",
            "risk": risk
        }
        
    except Exception as e:
        return {
            "domain": domain if 'domain' in locals() else url,
            "error": str(e),
            "creation_date": "Unknown",
            "days_alive": -1,
            "registrar": "Unknown",
            "risk": "Unknown"
        }
