import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, Model
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import joblib
from urllib.parse import urlparse
import os

# Define base directory for absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')

class MultiHeadSelfAttention(layers.Layer):
    def __init__(self, embed_dim, num_heads):
        super(MultiHeadSelfAttention, self).__init__()
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        
        assert embed_dim % num_heads == 0
        
        self.projection_dim = embed_dim // num_heads
        self.query_dense = layers.Dense(embed_dim)
        self.key_dense = layers.Dense(embed_dim)
        self.value_dense = layers.Dense(embed_dim)
        self.combine_heads = layers.Dense(embed_dim)
        
    def attention(self, query, key, value):
        score = tf.matmul(query, key, transpose_b=True)
        dim_key = tf.cast(tf.shape(key)[-1], tf.float32)
        scaled_score = score / tf.math.sqrt(dim_key)
        weights = tf.nn.softmax(scaled_score, axis=-1)
        output = tf.matmul(weights, value)
        return output, weights
    
    def separate_heads(self, x, batch_size):
        x = tf.reshape(x, (batch_size, -1, self.num_heads, self.projection_dim))
        return tf.transpose(x, perm=[0, 2, 1, 3])
    
    def call(self, inputs):
        batch_size = tf.shape(inputs)[0]
        
        query = self.query_dense(inputs)
        key = self.key_dense(inputs)
        value = self.value_dense(inputs)
        
        query = self.separate_heads(query, batch_size)
        key = self.separate_heads(key, batch_size)
        value = self.separate_heads(value, batch_size)
        
        attention, weights = self.attention(query, key, value)
        attention = tf.transpose(attention, perm=[0, 2, 1, 3])
        
        concat_attention = tf.reshape(attention, 
                                    (batch_size, -1, self.embed_dim))
        output = self.combine_heads(concat_attention)
        return output

def preprocess_url(url):
    """Extract and clean URL features"""
    try:
        parsed = urlparse(url)
        features = f"{parsed.scheme} {parsed.netloc} {parsed.path} {parsed.query} {parsed.fragment}"
        features = re.sub(r'[^\w\s\.]', ' ', features)
        features = re.sub(r'\s+', ' ', features.strip())
        return features.lower()
    except:
        return url.lower()

def preprocess_email(email_text):
    """Extract and clean email features"""
    try:
        # Remove HTML tags
        email_text = re.sub(r'<[^>]+>', ' ', email_text)
        
        # Remove URLs from email
        email_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' [URL] ', email_text)
        
        # Remove email addresses
        email_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' [EMAIL] ', email_text)
        
        # Remove phone numbers
        email_text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', ' [PHONE] ', email_text)
        
        # Remove excessive whitespace
        email_text = re.sub(r'\s+', ' ', email_text.strip())
        
        # Convert to lowercase
        return email_text.lower()
    except:
        return str(email_text).lower()

def build_phishing_model(vocab_size, max_length, embed_dim=128, num_heads=8):
    """Build Multihead Self-Attention model"""
    inputs = layers.Input(shape=(max_length,))
    
    # Embedding layer
    embedding = layers.Embedding(vocab_size, embed_dim, mask_zero=True)(inputs)
    
    # Positional encoding
    positions = tf.range(start=0, limit=max_length, delta=1)
    position_embedding = layers.Embedding(max_length, embed_dim)(positions)
    embedding += position_embedding
    
    # Multihead Self-Attention
    attention_output = MultiHeadSelfAttention(embed_dim, num_heads)(embedding)
    
    # Add & Norm
    attention_output = layers.Add()([embedding, attention_output])
    attention_output = layers.LayerNormalization()(attention_output)
    
    # Feed Forward Network
    ffn = layers.Dense(512, activation='relu')(attention_output)
    ffn = layers.Dense(embed_dim)(ffn)
    
    # Add & Norm
    ffn_output = layers.Add()([attention_output, ffn])
    ffn_output = layers.LayerNormalization()(ffn_output)
    
    # Global pooling and classification
    pooled = layers.GlobalAveragePooling1D()(ffn_output)
    dropout = layers.Dropout(0.3)(pooled)
    dense = layers.Dense(64, activation='relu')(dropout)
    outputs = layers.Dense(1, activation='sigmoid')(dense)
    
    model = Model(inputs=inputs, outputs=outputs)
    return model

# Suspicious keywords for heuristic analysis
SUSPICIOUS_KEYWORDS = [
    'urgent', 'immediate', 'act now', 'limited time', 'click here', 'verify account',
    'suspended', 'update payment', 'confirm identity', 'prize', 'winner', 'congratulations',
    'free', 'cash', 'money', 'lottery', 'inheritance', 'tax refund', 'refund',
    'phishing', 'suspicious', 'security alert', 'compromised', 'login', 'password',
    'credential', 'bank', 'account', 'verify', 'wallet', 'crypto', 'bitcoin'
]

def calculate_heuristic_score(text):
    """
    Calculate a comprehensive rule-based risk score (Hybrid Detection).
    Checks for:
    1. Suspicious Keywords (Content/Email)
    2. IP Address Usage (URL)
    3. URL Obfuscation (@)
    4. Excessive Special Characters (.-)
    5. Suspicious Length
    
    Returns:
        - score (0-100)
        - suspicious_words (list of words/triggers found)
    """
    text_lower = text.lower()
    found_triggers = []
    score = 0
    
    # 1. Suspicious Keyword Scanning
    for word in SUSPICIOUS_KEYWORDS:
        if word in text_lower:
            found_triggers.append(word)
            score += 15  # Increased weight for known phishing terms
            
    # TRUSTED DOMAIN CHECK
    # Reduce score for known safe TLDs/patterns if likely legitimate
    trusted_tlds = ['.ac.in', '.edu', '.gov', '.mil', '.org.in']
    for tld in trusted_tlds:
        if tld in text_lower:
            score -= 20 # Bonus for educational/gov sites
            # remove some triggers if they were false positives due to academic terms
            if "verify" in found_triggers: found_triggers.remove("verify") 
            if "account" in found_triggers: found_triggers.remove("account")
            
    score = max(0, score) # Ensure non-negative before adding other penalties
            
    # 2. Heuristics primarily for URLs (but applicable to text containing them)
    
    # Check for IP Address pattern (e.g., http://192.168.1.1)
    # Regex for basic IPv4
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    if re.search(ip_pattern, text_lower):
        # Discount standard local versions if needed, but usually suspicious in public URLs
        if "127.0.0.1" not in text_lower:
            score += 40
            found_triggers.append("ip_address_detected")

    # Check for URL Obfuscation (using '@' to hide domain)
    if "@" in text_lower and "mailto:" not in text_lower:
        # In a URL context, @ is often used for redirects or credential stuffing
        # In email, it's normal, so we need to be careful.
        # Simple heuristic: if it looks like a URL structure
        if "http" in text_lower:
            score += 30
            found_triggers.append("url_obfuscation_(@)")

    # Check for Excessive Special Characters (Typosquatting/Subdomain abuse)
    dot_count = text_lower.count('.')
    hyphen_count = text_lower.count('-')
    
    if dot_count > 4:
        score += 10
        found_triggers.append("deeply_nested_subdomain")
        
    if hyphen_count > 3:
        score += 10
        found_triggers.append("excessive_hyphens")

    # Check for Suspicious Length
    if len(text) > 75 and "http" in text_lower:
        score += 10
        found_triggers.append("suspicious_length")
            
    # Check for Multiple Links (Email context)
    link_count = text_lower.count('http')
    if link_count > 2:
        score += 15
        found_triggers.append("multiple_links")
        
    # Cap score at 100
    score = min(score, 100)
    
    return score, list(set(found_triggers))

def extract_email_features(email_text):
    """Extract additional features from email content"""
    features = {}
    
    # Use the shared heuristic function
    _, found_words = calculate_heuristic_score(email_text)
    features['suspicious_word_count'] = len(found_words)
    
    # URL and link analysis
    features['url_count'] = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', email_text))
    features['email_count'] = len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_text))
    
    # Text characteristics
    features['char_count'] = len(email_text)
    features['word_count'] = len(email_text.split())
    features['exclamation_count'] = email_text.count('!')
    features['question_count'] = email_text.count('?')
    features['dollar_count'] = email_text.count('$')
    
    # Capital letters ratio
    if len(email_text) > 0:
        features['caps_ratio'] = sum(1 for c in email_text if c.isupper()) / len(email_text)
    else:
        features['caps_ratio'] = 0
    
    return features

def predict_url(url, model_path=None, model=None, vectorizer=None):
    """Predict if URL is phishing or legitimate with explainability"""
    try:
        # Load model and components if not provided
        if model is None:
            if model_path is None:
                model_path = os.path.join(MODEL_DIR, 'phishing_model.h5')
            model = tf.keras.models.load_model(model_path, custom_objects={
                'MultiHeadSelfAttention': MultiHeadSelfAttention
            })
        
        if vectorizer is None:
            vectorizer = joblib.load(os.path.join(MODEL_DIR, 'vectorizer.pkl'))
        
        # Preprocess URL
        processed_url = preprocess_url(url)
        X = vectorizer.transform([processed_url]).toarray()
        
        # 1. Transformer Model Score
        prediction = model.predict(X, verbose=0)[0][0]
        transformer_score = float(prediction) * 100  # Convert to 0-100 scale
        
        # 2. Rule-Based Score
        rule_score, suspicious_words = calculate_heuristic_score(url)
        
        # 3. Final Hybrid Score
        # Weighted average: 70% Model, 30% Rules
        # But if model is very confident (>90%), trust it more
        if transformer_score > 90 or transformer_score < 10:
            final_score = (transformer_score * 0.9) + (rule_score * 0.1)
        else:
            final_score = (transformer_score * 0.7) + (rule_score * 0.3)
            
        final_score = min(max(final_score, 0), 100)
        
        # Determine Label based on Final Score
        if final_score > 50:
            label = "Phishing"
        else:
            label = "Legitimate"
        
        return {
            'prediction': label,
            'confidence': round(final_score, 2),
            'scores': {
                'transformer': round(transformer_score, 2),
                'rule_based': round(rule_score, 2),
                'final': round(final_score, 2)
            },
            'suspicious_words': suspicious_words,
            'input': url,
            'type': 'URL',
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'prediction': 'Error',
            'confidence': 0,
            'scores': {'transformer': 0, 'rule_based': 0, 'final': 0},
            'suspicious_words': [],
            'input': url,
            'type': 'URL',
            'error': str(e),
            'status': 'error'
        }

def predict_email(email_text, model_path=None, model=None, vectorizer=None):
    """Predict if email is phishing or legitimate with explainability"""
    try:
        # Load model and components if not provided
        if model is None:
            if model_path is None:
                model_path = os.path.join(MODEL_DIR, 'email_model.h5')
            model = tf.keras.models.load_model(model_path, custom_objects={
                'MultiHeadSelfAttention': MultiHeadSelfAttention
            })
            
        if vectorizer is None:
            vectorizer = joblib.load(os.path.join(MODEL_DIR, 'email_vectorizer.pkl'))
        
        # Preprocess email
        processed_email = preprocess_email(email_text)
        X = vectorizer.transform([processed_email]).toarray()
        
        # 1. Transformer Model Score
        prediction = model.predict(X, verbose=0)[0][0]
        transformer_score = float(prediction) * 100
        
        # 2. Rule-Based Score
        rule_score, suspicious_words = calculate_heuristic_score(email_text)
        
        # 3. Final Hybrid Score
        if transformer_score > 90 or transformer_score < 10:
            final_score = (transformer_score * 0.9) + (rule_score * 0.1)
        else:
            final_score = (transformer_score * 0.7) + (rule_score * 0.3)
            
        final_score = min(max(final_score, 0), 100)
        
        # Determine Label
        if final_score > 50:
            label = "Phishing"
        else:
            label = "Legitimate"
        
        # Extract additional features for analysis
        email_features = extract_email_features(email_text)
        
        return {
            'prediction': label,
            'confidence': round(final_score, 2),
            'scores': {
                'transformer': round(transformer_score, 2),
                'rule_based': round(rule_score, 2),
                'final': round(final_score, 2)
            },
            'suspicious_words': suspicious_words,
            'input': email_text[:200] + "..." if len(email_text) > 200 else email_text,
            'type': 'Email',
            'features': email_features,
            'status': 'success'
        }
        
    except Exception as e:
        return {
            'prediction': 'Error',
            'confidence': 0,
            'scores': {'transformer': 0, 'rule_based': 0, 'final': 0},
            'suspicious_words': [],
            'input': email_text[:200] + "..." if len(email_text) > 200 else email_text,
            'type': 'Email',
            'error': str(e),
            'status': 'error'
        }

def detect_input_type(input_text):
    """Automatically detect if input is URL or email content"""
    input_text = input_text.strip()
    
    # Check if it's a URL
    url_patterns = [
        r'^https?://',
        r'^www\.',
        r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.[a-zA-Z]{2,}',
    ]
    
    for pattern in url_patterns:
        if re.match(pattern, input_text, re.IGNORECASE):
            return 'URL'
    
    # Check if it's email content (look for email-like characteristics)
    email_indicators = [
        'subject:', 'from:', 'to:', 'dear', 'hello', 'hi,',
        'best regards', 'sincerely', 'thank you', 'please',
        'email', 'message', 'contact', 'reply'
    ]
    
    input_lower = input_text.lower()
    email_score = sum(1 for indicator in email_indicators if indicator in input_lower)
    
    # If it contains multiple email indicators or is long text, classify as email
    if email_score >= 2 or len(input_text) > 100:
        return 'Email'
    
    # Default to URL if uncertain
    return 'URL'

def predict_smart(input_text, url_model=None, url_vectorizer=None, email_model=None, email_vectorizer=None):
    """Smart prediction that auto-detects input type"""
    input_type = detect_input_type(input_text)
    
    if input_type == 'URL':
        return predict_url(input_text, model=url_model, vectorizer=url_vectorizer)
    else:
        return predict_email(input_text, model=email_model, vectorizer=email_vectorizer)
