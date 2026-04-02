from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse
import requests

def analyze_webpage(url):
    """
    Analyzes a webpage for both phishing behaviors AND legitimacy signals.
    
    Returns:
    dict: behavior_score (can be negative for very safe sites), flags, suspicious_words, legitimacy_signals
    """
    flags = []
    legitimacy_signals = []
    score = 0
    
    # Configure Chrome in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = None
    try:
        # 1. SSL Check (Simple check based on URL)
        is_https = url.startswith("https://")
        if not is_https:
            score += 15
            flags.append("Insecure connection (HTTP)")
        else:
            legitimacy_signals.append("Secure connection (HTTPS)")
            score -= 5 # Bonus for HTTPS
            
        # Initialize WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        
        # Access the page
        print(f"🔍 Visiting: {url}")
        driver.get(url)
        
        # Parse HTML
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        page_text = soup.get_text().lower()
        current_domain = urlparse(url).netloc
        
        # --- PHISHING INDICATORS ---
        
        # 2. Password input detection
        password_inputs = soup.find_all('input', type='password')
        if password_inputs:
            score += 40
            flags.append("Password input field detected")
            
        # 3. Forms submitting to external domains
        forms = soup.find_all('form')
        external_form_found = False
        for form in forms:
            action = form.get('action', '')
            if action and action.startswith('http'):
                action_domain = urlparse(action).netloc
                if action_domain and action_domain != current_domain:
                    # Ignore common payment/social integrations
                    trusted_actions = ['paypal.com', 'stripe.com', 'google.com', 'facebook.com']
                    if not any(t in action_domain for t in trusted_actions):
                        external_form_found = True
                        break
        if external_form_found:
            score += 30
            flags.append("Form submits to external/unverifiable domain")
            
        # 4. JavaScript redirects
        scripts = soup.find_all('script')
        redirect_keywords = ['window.location', 'location.href', 'location.replace', 'settimeout']
        for script in scripts:
            if script.string and any(k in script.string.lower() for k in redirect_keywords):
                if 'location.href' in script.string.lower() or 'location.replace' in script.string.lower():
                    score += 20
                    flags.append("Potential JavaScript redirect detected")
                    break

        # --- LEGITIMACY SIGNALS (Positive Signals to lower score) ---
        
        # A. Contact Information (Phone, Address patterns)
        # Simple regex for phone numbers
        import re
        phone_pattern = r'\+?(\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        if re.search(phone_pattern, page_text):
            score -= 20
            legitimacy_signals.append("Contact phone number found")
            
        # B. Social Media Presence
        social_domains = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'youtube.com']
        links = soup.find_all('a', href=True)
        found_socials = []
        for link in links:
            href = link['href']
            for sd in social_domains:
                if sd in href and sd not in current_domain:
                    found_socials.append(sd.split('.')[0])
        
        if len(set(found_socials)) >= 2:
            score -= 25
            legitimacy_signals.append(f"Multiple social media profiles linked: {', '.join(list(set(found_socials)))}")
        elif len(set(found_socials)) == 1:
            score -= 10
            legitimacy_signals.append("Social media profile linked")

        # C. Standard Business Pages
        standard_pages = {
            'about': ['about us', 'our story', 'company'],
            'contact': ['contact us', 'get in touch', 'support'],
            'privacy': ['privacy policy', 'privacy notice'],
            'terms': ['terms of service', 'terms and conditions']
        }
        
        found_pages = 0
        for category, keywords in standard_pages.items():
            if any(k in page_text for k in keywords):
                found_pages += 1
        
        if found_pages >= 3:
            score -= 30
            legitimacy_signals.append("Complete business profile (About, Contact, Privacy, Terms)")
        elif found_pages >= 1:
            score -= 10
            legitimacy_signals.append("Basic business links found")

        # D. Internal Link Consistency
        internal_links = 0
        total_links = 0
        for link in links:
            href = link['href']
            if href.startswith('/') or (current_domain in href):
                internal_links += 1
            total_links += 1
            
        if total_links > 10 and (internal_links / total_links) > 0.6:
            score -= 15
            legitimacy_signals.append("Consistent internal navigation")

        # 5. Suspicious Keyword Scanning (Updated list)
        SUSPICIOUS_KEYWORDS = [
            'urgent', 'act now', 'suspended', 'update payment', 'confirm identity', 
            'prize', 'winner', 'lottery', 'inheritance', 'tax refund',
            'security alert', 'compromised', 'credential', 'wallet', 'crypto'
        ]
        
        found_keywords = []
        for word in SUSPICIOUS_KEYWORDS:
             if word in page_text:
                 found_keywords.append(word)
                 score += 10
                 
        if found_keywords:
            flags.append(f"Suspicious tone detected: {', '.join(found_keywords[:3])}")
            
        # E. Website Purpose & Category Analysis
        categories = {
            'Educational': ['learn', 'course', 'student', 'university', 'training', 'education', 'academy', 'aptitude', 'school'],
            'E-commerce': ['buy', 'shop', 'cart', 'price', 'product', 'checkout', 'sale', 'store', 'shipping'],
            'Banking/Finance': ['bank', 'loan', 'invest', 'finance', 'credit', 'payment', 'transfer', 'savings', 'wallet'],
            'Corporate/Business': ['company', 'solutions', 'services', 'industry', 'partners', 'agency', 'enterprise', 'clients'],
            'Social Media': ['connect', 'friend', 'profile', 'post', 'share', 'follow', 'community', 'network'],
            'Portfolio/Personal': ['portfolio', 'my work', 'about me', 'developer', 'designer', 'blog', 'hobbies'],
            'Login Portal': ['sign in', 'login', 'portal', 'dashboard', 'members', 'access', 'authenticated']
        }
        
        # Calculate Category Scores
        cat_scores = {cat: 0 for cat in categories}
        for cat, keywords in categories.items():
            for k in keywords:
                if k in page_text:
                    cat_scores[cat] += 1
        
        # Determine Primary Category
        primary_category = max(cat_scores, key=cat_scores.get) if any(cat_scores.values()) else "Informational/General"
        
        # Site Summary/Purpose Generation
        title = soup.title.string.strip() if soup.title else "Untitled Website"
        meta_desc = soup.find("meta", {"name": "description"})
        meta_desc = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else ""
        
        # Design Intent Mapping
        design_intents = {
            'Educational': 'Knowledge Sharing & Student Engagement',
            'E-commerce': 'Product Showcase & Sales Conversion',
            'Banking/Finance': 'Secure Transactions & Financial Trust',
            'Corporate/Business': 'Professional Branding & Service Presentation',
            'Social Media': 'User Interaction & Community Building',
            'Portfolio/Personal': 'Self-Expression & Creative Display',
            'Login Portal': 'Identity Verification & Secure Access',
            'Informational/General': 'Content Delivery & User Information'
        }
        design_intent = design_intents.get(primary_category, 'Information Delivery')

        # Build Purpose Description
        purpose = f"Analyzing content indicates this is an **{primary_category}** platform."
        if meta_desc:
            purpose += f" The site describes itself as: '{meta_desc[:150]}...'"
        elif title != "Untitled Website":
            purpose += f" Based on the title '{title}', it appears to focus on {primary_category.lower()} services."
        else:
            purpose += f" The layout and keywords suggest it is used for {primary_category.lower()} purposes."

        # Final Score Normalization
        # Behavior score typically contributes 10-20% to final score.
        # We allow it to be negative to act as a "Reliability Bonus" for safe sites.
        
        return {
            "behavior_score": score,
            "flags": flags,
            "legitimacy_signals": legitimacy_signals,
            "suspicious_words": found_keywords,
            "website_purpose": purpose,
            "website_category": primary_category,
            "design_intent": design_intent,
            "website_title": title,
            "is_live": True
        }
        
    except Exception as e:
        print(f"Crawler error: {e}")
        return {
            "behavior_score": 0,
            "flags": [f"Visual analysis failed: {str(e)}"],
            "legitimacy_signals": [],
            "suspicious_words": [],
            "website_purpose": "Site visit failed, purpose could not be determined.",
            "website_category": "Unknown",
            "is_live": False
        }
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
