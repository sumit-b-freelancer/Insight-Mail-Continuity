from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q
from .models import Email, AnalysisResult
from .ai_engine import analyze_email_content

@receiver(post_save, sender=Email)
def auto_analyze_email(sender, instance, created, **kwargs):
    if created:
        print(f"⚡ Analyzing for: {instance.recipient.username}...")
        
        # 1. FETCH HISTORY
        previous_emails = Email.objects.filter(
            (Q(sender=instance.sender) & Q(recipient=instance.recipient)) |
            (Q(sender=instance.recipient) & Q(recipient=instance.sender))
        ).exclude(id=instance.id).order_by('-received_at')[:3]

        history_data = [{'sender': e.sender.username, 'body': e.body} for e in previous_emails]
        
        # 2. GET USER NAME
        if instance.recipient.first_name:
            my_name = f"{instance.recipient.first_name} {instance.recipient.last_name}"
        else:
            my_name = instance.recipient.username

        # --- FIX IS HERE ---
        # OLD: analyze_email_content(instance.subject, instance.body, history=..., agent_name=...)
        # NEW: Just pass 'instance'
        
        analysis_data = analyze_email_content(
            instance,                 # <--- ONLY PASS THE OBJECT
            history=history_data, 
            agent_name=my_name
        )
        
        # 4. SAVE RESULT
        AnalysisResult.objects.create(
            email=instance,
            summary=analysis_data['summary'],
            sentiment=analysis_data['sentiment'],
            tone=analysis_data['tone'],
            risk_score=analysis_data['risk_score'],
            suggested_category=analysis_data['suggested_category'],
            suggested_reply=analysis_data['suggested_reply']
        )
        
        instance.is_analyzed = True
        instance.save(update_fields=['is_analyzed'])