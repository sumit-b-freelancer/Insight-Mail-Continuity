import os
import pickle
import numpy as np
import pandas as pd
from datetime import timedelta
from sklearn.svm import SVR
from django.db.models import Q
from django.conf import settings
from .models import Email

# Path to save/load the trained SVR model
SVR_MODEL_PATH = os.path.join(settings.BASE_DIR, 'ml_models', 'svr_model.pkl')

class EngagementEngine:
    def __init__(self):
        self.model = self._load_model()

    def _load_model(self):
        """Loads the trained SVR model if it exists."""
        try:
            with open(SVR_MODEL_PATH, 'rb') as f:
                return pickle.load(f)
        except (FileNotFoundError, EOFError):
            return None

    def get_thread_features(self, email_obj):
        """
        Research Phase 2: Feature Extraction
        Calculates Rc (Reply Count), Fc (Forward Count), and T (Time Span).
        """
        # 1. Group by Subject (Simple Threading)
        # Normalize subject: Remove 'Re:', 'Fwd:' to find the root conversation
        root_subject = email_obj.subject.replace("Re:", "").replace("Fwd:", "").strip()
        
        # Fetch all emails in this thread (sent or received by these users)
        thread_emails = Email.objects.filter(
            subject__icontains=root_subject
        ).order_by('received_at')

        if not thread_emails.exists():
            return [0, 0, 0]

        # 2. Calculate Features
        # Rc: Count emails starting with "Re:" (Replies)
        reply_count = thread_emails.filter(subject__istartswith="Re:").count()
        
        # Fc: Count emails starting with "Fwd:" (Forwards)
        forward_count = thread_emails.filter(subject__istartswith="Fwd:").count()
        
        # T: Time Span (Hours)
        start_time = thread_emails.first().received_at
        end_time = thread_emails.last().received_at
        duration = (end_time - start_time).total_seconds() / 3600 # Convert to hours

        return [reply_count, forward_count, duration]

    def predict_engagement(self, email_obj):
        """
        Predicts if the email is 'Interested', 'Uninterested', or 'Individual'.
        Returns: Class Label (str)
        """
        features = self.get_thread_features(email_obj) # [Rc, Fc, T]
        
        # IF MODEL IS TRAINED: Use SVR
        if self.model:
            # SVR requires 2D array: [[Rc, Fc, T]]
            prediction_score = self.model.predict([features])[0]
            
            # Map Score to Class (Thresholds from Research)
            # Assuming we trained 1=Interested, 0.5=Uninterested, 0=Individual
            if prediction_score > 0.7:
                return "Interested"
            elif prediction_score > 0.3:
                return "Uninterested"
            else:
                return "Individual"

        # FALLBACK (Rule-Based) if model not trained yet
        # Research Logic: "Interested" if Replies > 2 and Forwards > 0
        rc, fc, t = features
        if rc > 2 and fc > 0:
            return "Interested"
        elif rc >= 1 or t < 24:
            return "Uninterested"
        else:
            return "Individual"