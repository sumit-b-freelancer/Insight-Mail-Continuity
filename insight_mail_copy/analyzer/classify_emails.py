import os
import django
import pickle
import numpy as np

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insight_mail_copy.settings') # <--- CHECK YOUR PROJECT NAME
django.setup()

from your_app_name.models import Email
from your_app_name.engagement_engine import EngagementEngine

def classify_inbox():
    print("--- Phase 3: AI Email Classification ---")
    
    # 1. Load the Trained Model
    model_path = os.path.join('ml_models', 'svr_model.pkl')
    try:
        with open(model_path, 'rb') as f:
            svr_model = pickle.load(f)
        print("Model loaded successfully.")
    except FileNotFoundError:
        print("Error: Model not found! Run train_svr.py first.")
        return

    engine = EngagementEngine()
    emails = Email.objects.filter(classification="Unclassified") # Only process new ones

    if not emails.exists():
        print("All emails are already classified!")
        return

    print(f"Classifying {emails.count()} emails...")
    
    count = 0
    for email in emails:
        # 2. Extract Features (Same as training)
        features = engine.get_thread_features(email) # Returns [Rc, Fc, T]
        
        # 3. Predict Priority
        # Reshape because model expects a list of lists [[x1, x2, x3]]
        prediction = svr_model.predict([features])[0]
        
        # 4. Assign Label based on Score
        email.priority_score = prediction
        
        if prediction > 0.7:
            email.classification = "Important"
        elif prediction > 0.3:
            email.classification = "Casual"
        else:
            email.classification = "Low Priority"
            
        email.save()
        count += 1
        
        if count % 10 == 0:
            print(f"Processed {count} emails...")

    print(f"--- Done! Classified {count} emails. ---")

if __name__ == "__main__":
    classify_inbox()
