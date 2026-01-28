from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Email, AnalysisResult
from .forms import SignUpForm, ComposeEmailForm # <--- Make sure to import SignUpForm
from .utils import fetch_gmail_emails # Import the tool we just made

@login_required
def sync_gmail_view(request):
    # FOR HACKATHON: Hardcode credentials or put in settings.py
    # DO NOT commit real passwords to GitHub
    GMAIL_USER = "mgumathannavar@gmail.com"
    GMAIL_APP_PASSWORD = "rran vxwr wmxr tnod" # <--- Your 16-char App Password

    if request.method == "POST":
        message = fetch_gmail_emails(GMAIL_USER, GMAIL_APP_PASSWORD, request.user)
        # Store message in session to show on dashboard (optional)
        print(message) 
        return redirect('dashboard')
    
    return redirect('dashboard')

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST) # <--- Use the new form
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm() # <--- Use the new form
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

# --- EMAIL SYSTEM VIEWS ---

@login_required
def dashboard(request):
    """Acts as the INBOX (Emails received by the user)"""
    # Filter: Recipient = Current User
    emails = Email.objects.filter(recipient=request.user).order_by('-received_at')
    
    total_emails = emails.count()
    # Filter High Risk in MY inbox
    high_risk_count = AnalysisResult.objects.filter(email__recipient=request.user, risk_score__gt=50).count()
    
    context = {
        'emails': emails,
        'box_type': 'Inbox',
        'total_emails': total_emails,
        'high_risk_count': high_risk_count
    }
    return render(request, 'dashboard.html', context)

@login_required
def sent_box(request):
    """Acts as SENT ITEMS (Emails sent by the user)"""
    emails = Email.objects.filter(sender=request.user).order_by('-received_at')
    
    context = {
        'emails': emails,
        'box_type': 'Sent',
        'total_emails': emails.count(),
        'high_risk_count': 0 # We don't usually count risk on sent items
    }
    return render(request, 'dashboard.html', context)

@login_required
def compose_email(request):
    users = User.objects.exclude(id=request.user.id)
    
    # NEW: Check if we are replying (Pre-fill data)
    # We get these from the URL (e.g., ?to=boss&subject=Re:Hello)
    prefill_to = request.GET.get('to', '')
    prefill_subject = request.GET.get('subject', '')
    
    if request.method == 'POST':
        username_input = request.POST.get('recipient_username')
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        
        try:
            recipient_user = User.objects.get(username=username_input)
            Email.objects.create(
                sender=request.user,
                recipient=recipient_user,
                subject=subject,
                body=body
            )
            return redirect('dashboard')
        except User.DoesNotExist:
            return render(request, 'compose.html', {
                'users': users, 
                'error': f"User '{username_input}' not found.",
                'prefill_to': username_input,    # Keep what they typed
                'prefill_subject': subject       # Keep what they typed
            })

    # Pass the pre-fill variables to the template
    return render(request, 'compose.html', {
        'users': users,
        'prefill_to': prefill_to,
        'prefill_subject': prefill_subject
    })

@login_required
def email_detail(request, email_id):
    email = get_object_or_404(Email, id=email_id)
    
    # Security check
    if email.sender != request.user and email.recipient != request.user:
        return redirect('dashboard')
    
    # NEW: Mark as read if I am the recipient
    if request.user == email.recipient and not email.is_read:
        email.is_read = True
        email.save()
        
    return render(request, 'email_detail.html', {'email': email})

@login_required
def analyze_email(request, email_id):
    from .ai_engine import analyze_email_content
    email = get_object_or_404(Email, id=email_id)
    
    # --- FIX IS HERE ---
    # OLD: analysis_data = analyze_email_content(email.subject, email.body)
    # NEW: Just pass 'email'
    analysis_data = analyze_email_content(email) 
    
    AnalysisResult.objects.update_or_create(
        email=email,
        defaults={
            'summary': analysis_data['summary'],
            'sentiment': analysis_data['sentiment'],
            'tone': analysis_data['tone'],
            'risk_score': analysis_data['risk_score'],
            'suggested_category': analysis_data['suggested_category'],
            'suggested_reply': analysis_data['suggested_reply'],
        }
    )
    email.is_analyzed = True
    email.save()
    return redirect('dashboard')