from django.db import models
from django.contrib.auth.models import User

class Email(models.Model):
    # Link to the actual User accounts
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_emails')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_emails')
    
    subject = models.CharField(max_length=255)
    body = models.TextField()
    received_at = models.DateTimeField(auto_now_add=True)
    
    is_analyzed = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    priority_score = models.FloatField(default=0.0) # The raw AI score (0.0 to 1.0)
    classification = models.CharField(max_length=20, default="Unclassified") # The human label
    
    def __str__(self):
        return f"{self.sender} -> {self.recipient}: {self.subject}"

class AnalysisResult(models.Model):
    email = models.OneToOneField(Email, on_delete=models.CASCADE, related_name='analysis')
    summary = models.TextField()
    sentiment = models.CharField(max_length=50)
    tone = models.CharField(max_length=50)
    risk_score = models.IntegerField(default=0)
    flagged_keywords = models.CharField(max_length=255, blank=True, null=True)
    suggested_category = models.CharField(max_length=50, default="inquiry")
    suggested_reply = models.TextField(blank=True)
    

    created_at = models.DateTimeField(auto_now_add=True)
