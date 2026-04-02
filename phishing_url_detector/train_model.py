import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import os
from model_utils import preprocess_url, preprocess_email
import tensorflow as tf

def load_email_dataset():
    """Load/create phishing email dataset"""
    print("Creating email dataset...")
    
    try:
        # Expanded and more diverse sample phishing email data
        phishing_emails = [
            "URGENT: Your account has been suspended. Click here to verify immediately!",
            "Congratulations! You've won $10,000. Claim your prize now by clicking this link!",
            "Security Alert: Suspicious activity detected on your account. Update your password immediately or face permanent suspension.",
            "Your PayPal account will be closed within 24 hours. Verify your information to keep it active and avoid fees.",
            "Final Notice: Tax refund of $2,847 pending approval. Click to claim now before deadline expires.",
            "Bank Account Suspended: Immediate action required to restore access to your funds and services.",
            "You have received a wire transfer of $50,000 from overseas. Click to accept this payment immediately.",
            "Apple ID locked due to suspicious activity from unknown device. Verify to unlock and prevent data loss.",
            "Your credit card has been charged $599 for unauthorized purchase. Dispute this charge here within 24 hours.",
            "Amazon Prime membership expired. Click to renew immediately and avoid service interruption and late fees.",
            "From: security@paypaI.com\nSubject: Account Verification Required\nDear valued customer, your account requires immediate verification to prevent closure.",
            "From: noreply@bank-update.com\nSubject: Security Alert\nWe detected multiple suspicious login attempts from unknown locations. Verify your identity now.",
            "From: support@amazon-security.net\nSubject: Order Confirmation\nYour order of $899 has been processed and charged. Cancel here if not authorized by you.",
            "WARNING: Your bank account shows unusual activity. Verify identity now or account will be frozen permanently within hours.",
            "Free iPhone 15 Pro Max waiting for you! Limited time offer expires today. Click here to claim your free device now.",
            "IRS Notice: You qualify for additional tax refund of $3,247. Secure payment requires verification of personal information immediately.",
            "Microsoft Security Alert: Your computer has been infected with dangerous virus. Download our tool to remove threats now.",
            "Netflix Account Suspended: Payment method declined. Update billing information immediately to restore streaming services and avoid cancellation.",
            "Google Account Compromised: Unauthorized access detected from Russia. Change password now to secure your data and prevent theft.",
            "WhatsApp Verification Code: 847293 expires in 5 minutes. Enter code to verify account or lose access permanently to messages.",
            "Your package delivery failed. Pay $2.99 shipping fee to reschedule delivery or item will be returned to sender.",
            "Social Security Administration Notice: Your SSN has been suspended due to suspicious activity. Call immediately to restore.",
            "Bitcoin Investment Opportunity: Turn $500 into $50,000 in 30 days. Limited spots available. Join now before it's too late.",
            "Dating Site Match: Beautiful woman wants to meet you. Click profile to chat now and find your soulmate today.",
            "Lottery Winner: You won $1,000,000 in international lottery. Claim prize by providing bank details for direct deposit.",
        ] * 300  # Multiply to get more variety
        
        legitimate_emails = [
            "Hi John, hope you're doing well. Let's schedule a meeting for next week to discuss the project progress and next steps.",
            "Thank you for your recent purchase from our store. Your order #12345 has been processed and will arrive tomorrow morning.",
            "Your monthly bank statement is now available in your online account dashboard. You can view and download it anytime.",
            "Reminder: Team meeting scheduled for tomorrow at 2 PM in conference room A. Please bring your progress reports.",
            "Welcome to our newsletter! Here are this week's top articles about technology trends and industry insights for professionals.",
            "Your appointment with Dr. Smith is confirmed for Monday at 3 PM. Please arrive 15 minutes early for check-in.",
            "Thank you for contacting our customer support team. We have successfully resolved your technical issue as requested.",
            "Your software update has been completed successfully. The new version includes security improvements and bug fixes.",
            "Happy birthday! Hope you have a wonderful day celebrating with family and friends. Enjoy your special day!",
            "Your subscription renewal date is approaching next month. No action needed - payment will be processed automatically.",
            "From: service@paypal.com\nSubject: Monthly Statement Available\nYour PayPal monthly statement for March is now available for download.",
            "From: notifications@amazon.com\nSubject: Order Shipped\nGreat news! Your order has been shipped and will arrive by tomorrow evening.",
            "From: team@company.com\nSubject: Weekly Team Update\nHere's this week's project update and important team announcements for everyone.",
            "Meeting notes from yesterday's conference call are attached. Please review and provide feedback by end of week.",
            "Your gym membership will expire next month. Visit our website to renew online or stop by the front desk.",
            "Flight confirmation for your trip to New York. Check-in opens 24 hours before departure. Have a safe journey.",
            "Thank you for your donation to our charity. Your contribution will help us continue our important community work.",
            "Your online course has been successfully completed. Certificate will be mailed within 2-3 business days.",
            "Reminder: Car maintenance appointment scheduled for Friday at 10 AM. Please bring your vehicle registration.",
            "Your streaming service subscription continues next month. Enjoy unlimited access to movies and TV shows.",
            "Congratulations on your work anniversary! Thank you for your dedication and valuable contributions to our team.",
            "Weather alert: Snow expected tomorrow morning. Drive carefully and allow extra time for your commute to work.",
            "Your library books are due next Tuesday. You can renew them online or bring them to any branch location.",
            "Invitation: Company holiday party on December 15th at 6 PM. RSVP by December 1st to confirm attendance.",
            "Your prescription is ready for pickup at our pharmacy. Store hours are Monday through Friday 9 AM to 7 PM.",
        ] * 300  # Multiply to get more variety
        
        # Create DataFrame
        email_data = []
        
        # Add phishing emails
        for email in phishing_emails:
            email_data.append({'email_text': email, 'label': 'Phishing'})
        
        # Add legitimate emails
        for email in legitimate_emails:
            email_data.append({'email_text': email, 'label': 'Legitimate'})
        
        df = pd.DataFrame(email_data)
        
        print(f"Email dataset created with {len(df)} samples")
        print(f"Label distribution:\n{df['label'].value_counts()}")
        
        return df
        
    except Exception as e:
        print(f"Error creating email dataset: {e}")
        return None

def train_email_model():
    """Train email classification model"""
    print("\n" + "="*50)
    print("🚀 Training Email Classification Model...")
    print("="*50)
    
    # Load email data
    email_data = load_email_dataset()
    if email_data is None:
        print("Failed to load email data")
        return False
    
    # Preprocess emails
    print("Preprocessing emails...")
    email_data['processed_email'] = email_data['processed_email_text'] = email_data['email_text'].apply(preprocess_email)
    
    # Create TF-IDF features for emails - Fixed parameters
    email_vectorizer = TfidfVectorizer(
        max_features=3000,  # Reduced but realistic number
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1,  # Reduced to capture more features
        max_df=0.98,  # Increased to capture more features
        lowercase=True,
        token_pattern=r'\b\w+\b'
    )
    
    X_email = email_vectorizer.fit_transform(email_data['processed_email']).toarray()
    print(f"TF-IDF features shape: {X_email.shape}")
    
    # Ensure we have the expected number of features
    actual_features = X_email.shape[1]
    
    # Encode labels
    email_le = LabelEncoder()
    y_email = email_le.fit_transform(email_data['label'])
    
    # Split data
    X_train_email, X_test_email, y_train_email, y_test_email = train_test_split(
        X_email, y_email, test_size=0.2, random_state=42, stratify=y_email
    )
    
    print(f"Email training set: {X_train_email.shape[0]} samples")
    print(f"Email test set: {X_test_email.shape[0]} samples")
    print(f"Features per sample: {actual_features}")
    
    # Build email model with correct input shape
    email_model = tf.keras.Sequential([
        tf.keras.layers.Dense(256, activation='relu', input_shape=(actual_features,)),  # Use actual features
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    email_model.compile(
        optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.001),  # Reduced learning rate
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"Model input shape: {email_model.input_shape}")
    print(f"Model parameters: {email_model.count_params():,}")
    
    # Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', 
            patience=5, 
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', 
            factor=0.5, 
            patience=3,
            min_lr=1e-6,
            verbose=1
        )
    ]
    
    # Train email model
    print("Training email model...")
    email_history = email_model.fit(
        X_train_email, y_train_email,
        batch_size=32,  # Reduced batch size
        epochs=20,
        validation_data=(X_test_email, y_test_email),
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate email model
    y_pred_email = (email_model.predict(X_test_email, verbose=0) > 0.5).astype(int)
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
    
    email_accuracy = accuracy_score(y_test_email, y_pred_email)
    email_precision = precision_score(y_test_email, y_pred_email, average='binary')
    email_recall = recall_score(y_test_email, y_pred_email, average='binary')
    email_f1 = f1_score(y_test_email, y_pred_email, average='binary')
    
    print(f"\n=== Email Model Performance ===")
    print(f"Accuracy: {email_accuracy:.4f} ({email_accuracy*100:.2f}%)")
    print(f"Precision: {email_precision:.4f} ({email_precision*100:.2f}%)")
    print(f"Recall: {email_recall:.4f} ({email_recall*100:.2f}%)")
    print(f"F1-Score: {email_f1:.4f} ({email_f1*100:.2f}%)")
    
    print(f"\n=== Classification Report ===")
    print(classification_report(y_test_email, y_pred_email, target_names=['Legitimate', 'Phishing']))
    
    # Save email model and components
    os.makedirs('models', exist_ok=True)
    email_model.save('models/email_model.h5')
    joblib.dump(email_vectorizer, 'models/email_vectorizer.pkl')
    joblib.dump(email_le, 'models/email_label_encoder.pkl')
    
    # Save email model info
    email_model_info = {
        'accuracy': float(email_accuracy),
        'precision': float(email_precision),
        'recall': float(email_recall),
        'f1_score': float(email_f1),
        'training_samples': len(X_train_email),
        'test_samples': len(X_test_email),
        'features': actual_features,
        'model_type': 'email_classification',
        'epochs_trained': len(email_history.history['accuracy'])
    }
    
    joblib.dump(email_model_info, 'models/email_model_info.pkl')
    
    print("✅ Email model saved successfully!")
    print(f"📁 Model size: {os.path.getsize('models/email_model.h5')/1024/1024:.1f} MB")
    return True

def load_and_prepare_url_data():
    """Load URL datasets"""
    print("Loading URL datasets...")
    
    try:
        phishing_data = None
        legitimate_data = None
        
        # Load phishing URLs
        base_dir = os.path.dirname(os.path.abspath(__file__))
        phishing_file = os.path.join(base_dir, 'Phishing URL dataset', 'Phishing URLs.csv')
        
        if os.path.exists(phishing_file):
            try:
                df_phishing = pd.read_csv(phishing_file)
            except Exception:
                # Try with different encoding if default fails
                 df_phishing = pd.read_csv(phishing_file, encoding='latin-1')
                 
            print(f"Loaded Phishing URLs.csv with {df_phishing.shape[0]} samples")
            
            if 'url' in df_phishing.columns:
                phishing_data = df_phishing[['url']].copy()
            elif 'URL' in df_phishing.columns:
                phishing_data = df_phishing[['URL']].copy()
                phishing_data.columns = ['url']
            elif len(df_phishing.columns) >= 1:
                phishing_data = df_phishing.iloc[:, [0]].copy()
                phishing_data.columns = ['url']
            
            if phishing_data is not None:
                phishing_data['label'] = 'Phishing'
        
        # Load legitimate URLs
        legitimate_file = os.path.join(base_dir, 'Phishing URL dataset', 'Legitimate URLs.csv')
        
        if os.path.exists(legitimate_file):
            try:
                df_legitimate = pd.read_csv(legitimate_file)
            except Exception:
                df_legitimate = pd.read_csv(legitimate_file, encoding='latin-1')

            print(f"Loaded Legitimate URLs.csv with {df_legitimate.shape[0]} samples")
            
            if 'url' in df_legitimate.columns:
                legitimate_data = df_legitimate[['url']].copy()
            elif 'URL' in df_legitimate.columns:
                legitimate_data = df_legitimate[['URL']].copy()
                legitimate_data.columns = ['url']
            elif len(df_legitimate.columns) >= 1:
                legitimate_data = df_legitimate.iloc[:, [0]].copy()
                legitimate_data.columns = ['url']
            
            if legitimate_data is not None:
                legitimate_data['label'] = 'Legitimate'
        
    # Combine datasets
        data_frames = []
        if phishing_data is not None and legitimate_data is not None:
            # Sample to balance dataset - INCREASED SIZE for better accuracy
            # Use maximum available balanced data up to a reasonable limit
            min_len = min(len(phishing_data), len(legitimate_data))
            sample_size = min(150000, min_len)  # Increased cap to 150k or max available
            
            print(f"Balancing dataset to {sample_size} samples per class...")
            
            phishing_data = phishing_data.sample(n=sample_size, random_state=42)
            legitimate_data = legitimate_data.sample(n=sample_size, random_state=42)
            
            data_frames.append(phishing_data)
            data_frames.append(legitimate_data)
        
        if not data_frames:
            raise Exception("Could not find or load URL dataset files")
        
        data = pd.concat(data_frames, ignore_index=True)
        data = data.drop_duplicates(subset=['url']).reset_index(drop=True)
        data = data.dropna()
        data = data[data['url'].str.len() > 10]
        
        print(f"Final URL dataset: {len(data)} samples")
        print(f"Label distribution:\n{data['label'].value_counts()}")
        
        return data
        
    except Exception as e:
        print(f"Error loading URL dataset: {e}")
        return None

def train_url_model():
    """Train URL classification model"""
    print("\n" + "="*50)
    print("🚀 Training URL Classification Model...")
    print("="*50)
    
    # Load URL data
    url_data = load_and_prepare_url_data()
    if url_data is None:
        print("Failed to load URL data")
        return False
    
    # Preprocess URLs
    print("Preprocessing URLs...")
    url_data['processed_url'] = url_data['url'].apply(preprocess_url)
    
    # Create TF-IDF features with fixed parameters
    url_vectorizer = TfidfVectorizer(
        max_features=10000,  # Increased to capture more unique phishing patterns
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        lowercase=True,
        token_pattern=r'\b\w+\b'
    )
    
    X_url = url_vectorizer.fit_transform(url_data['processed_url']).toarray()
    print(f"URL TF-IDF features shape: {X_url.shape}")
    
    actual_features = X_url.shape[1]
    
    # Encode labels
    url_le = LabelEncoder()
    y_url = url_le.fit_transform(url_data['label'])
    
    # Split data
    X_train_url, X_test_url, y_train_url, y_test_url = train_test_split(
        X_url, y_url, test_size=0.2, random_state=42, stratify=y_url
    )
    
    print(f"URL training set: {X_train_url.shape[0]} samples")
    print(f"URL test set: {X_test_url.shape[0]} samples")
    print(f"Features per sample: {actual_features}")
    
    # Build URL model with correct input shape
    url_model = tf.keras.Sequential([
        tf.keras.layers.Dense(512, activation='relu', input_shape=(actual_features,)),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.4),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.Dropout(0.3),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    url_model.compile(
        optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.001),
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"URL Model parameters: {url_model.count_params():,}")
    
    # Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss', 
            patience=8, 
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss', 
            factor=0.5, 
            patience=3,
            min_lr=1e-6,
            verbose=1
        )
    ]
    
    # Train URL model
    print("Training URL model...")
    url_history = url_model.fit(
        X_train_url, y_train_url,
        batch_size=64,
        epochs=30,  # Increased epochs
        validation_data=(X_test_url, y_test_url),
        callbacks=callbacks,
        verbose=1
    )
    
    # Evaluate URL model
    y_pred_url = (url_model.predict(X_test_url, verbose=0) > 0.5).astype(int)
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
    
    url_accuracy = accuracy_score(y_test_url, y_pred_url)
    url_precision = precision_score(y_test_url, y_pred_url, average='binary')
    url_recall = recall_score(y_test_url, y_pred_url, average='binary')
    url_f1 = f1_score(y_test_url, y_pred_url, average='binary')
    
    print(f"\n=== URL Model Performance ===")
    print(f"Accuracy: {url_accuracy:.4f} ({url_accuracy*100:.2f}%)")
    print(f"Precision: {url_precision:.4f} ({url_precision*100:.2f}%)")
    print(f"Recall: {url_recall:.4f} ({url_recall*100:.2f}%)")
    print(f"F1-Score: {url_f1:.4f} ({url_f1*100:.2f}%)")
    
    print(f"\n=== Classification Report ===")
    print(classification_report(y_test_url, y_pred_url, target_names=['Legitimate', 'Phishing']))
    
    # Save URL model and components
    url_model.save('models/phishing_model.h5')  # Keep same name for compatibility
    joblib.dump(url_vectorizer, 'models/vectorizer.pkl')
    joblib.dump(url_le, 'models/label_encoder.pkl')
    
    url_model_info = {
        'accuracy': float(url_accuracy),
        'precision': float(url_precision),
        'recall': float(url_recall),
        'f1_score': float(url_f1),
        'training_samples': len(X_train_url),
        'test_samples': len(X_test_url),
        'features': actual_features,
        'model_type': 'url_classification',
        'epochs_trained': len(url_history.history['accuracy'])
    }
    
    joblib.dump(url_model_info, 'models/model_info.pkl')
    
    print("✅ URL model saved successfully!")
    print(f"📁 Model size: {os.path.getsize('models/phishing_model.h5')/1024/1024:.1f} MB")
    return True

def train_both_models():
    """Train both URL and Email models"""
    print("🛡️  Multi-Modal Phishing Detection System Training")
    print("🤖 Training Both URL and Email Classification Models")
    print("=" * 60)
    
    # Train email model
    email_success = train_email_model()
    
    # Train URL model if email training succeeded
    if email_success:
        url_success = train_url_model()
    else:
        url_success = False
    
    if email_success and url_success:
        print(f"\n{'='*60}")
        print("🎉 BOTH MODELS TRAINED SUCCESSFULLY! 🎉")
        print("="*60)
        print("✅ Email phishing detection model ready!")
        print("✅ URL phishing detection model ready!")
        print("🚀 Run 'python app.py' to start the web application")
        print("🌐 Now supports both URL and email analysis!")
        return True
    else:
        print(f"\n{'='*60}")
        print("❌ TRAINING FAILED")
        print("="*60)
        if not email_success:
            print("❌ Email model training failed")
        if not url_success:
            print("❌ URL model training failed")
        return False

if __name__ == "__main__":
    train_both_models()
