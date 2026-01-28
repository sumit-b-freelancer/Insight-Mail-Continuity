import os
import django
import pickle
import numpy as np
from sklearn.svm import SVR

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insight_mail.settings') # <--- CHANGE THIS
django.setup()

from analyzer.models import Email # <--- CHANGE THIS
from analyzer.engagement_engine import EngagementEngine

def train_svr():
    print("--- Phase 2: Training SVR Engagement Model ---")
    
    engine = EngagementEngine()
    emails = Email.objects.all()
    
    if not emails.exists():
        print("No emails to train on! Sync some emails first.")
        return

    X = [] # Features [Rc, Fc, T]
    y = [] # Labels (0, 0.5, 1.0)

    print(f"Extracting features from {emails.count()} emails...")
    
    for email in emails:
        features = engine.get_thread_features(email)
        X.append(features)
        
        # AUTO-LABELING (Creating Training Data)
        # Since we don't have human labels, we use the Research Rules to create "Ground Truth"
        rc, fc, t = features
        
        if rc > 2 and fc > 0:
            label = 1.0 # Interested
        elif rc >= 1:
            label = 0.5 # Uninterested
        else:
            label = 0.0 # Individual
            
        y.append(label)

    # Train SVR
    print("Training SVR Model...")
    svr = SVR(kernel='rbf', C=1.0, epsilon=0.1)
    svr.fit(X, y)
    
    # Save Model
    save_path = os.path.join('ml_models', 'svr_model.pkl')
    os.makedirs('ml_models', exist_ok=True) # Ensure folder exists
    with open(save_path, 'wb') as f:
        pickle.dump(svr, f)
        
    print(f"Model saved to {save_path}")
    print("--- Training Complete! ---")

if __name__ == "__main__":
    train_svr()