import whois
from datetime import datetime
from urllib.parse import urlparse

def get_domain_info(url):
    """
    Retrieves WHOIS information for a given URL and calculates a risk score based on domain age.
    """
    info = {
        "creation_date": "Unknown",
        "domain_age_days": 0,
        "registrar": "Unknown",
        "risk_score": 0
    }
    
    try:
        domain = urlparse(url).netloc
        if not domain:
            if "/" in url:
                domain = url.split("/")[0]
            else:
                domain = url
        
        # Remove www.
        if domain.startswith("www."):
            domain = domain[4:]
            
        # WHOIS lookup
        w = whois.whois(domain)
        
        # Extract registrar
        if w.registrar:
            # Handle list of registrars
            if isinstance(w.registrar, list):
                info["registrar"] = w.registrar[0]
            else:
                info["registrar"] = w.registrar
            
        # Extract creation date
        creation_date = w.creation_date
        
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if creation_date:
            info["creation_date"] = creation_date.strftime('%Y-%m-%d')
            
            # Calculate age
            now = datetime.now().replace(tzinfo=None)
            if creation_date.tzinfo:
                creation_date = creation_date.replace(tzinfo=None)
                
            age = now - creation_date
            info["domain_age_days"] = age.days
            
            # Risk Scoring
            if age.days < 30:
                info["risk_score"] = 80  # High Risk
            elif age.days < 180:
                info["risk_score"] = 50  # Suspicious
            else:
                info["risk_score"] = 10  # Likely Safe
                
    except Exception as e:
        # Handle missing WHOIS gracefully
        print(f"WHOIS lookup failed: {e}")
        
    return info
