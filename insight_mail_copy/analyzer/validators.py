import dns.resolver
from django.core.exceptions import ValidationError

def validate_email_existence(email):
    """
    Checks if the domain of the email address actually has valid MX (Mail Exchange) records.
    """
    try:
        domain = email.split('@')[1]
        
        # Query DNS for 'MX' records (Mail Exchange)
        records = dns.resolver.resolve(domain, 'MX')
        
        # If we get records back, the domain exists and can receive email!
        return True
        
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.LifetimeTimeout):
        # NXDOMAIN = Domain doesn't exist (e.g., gmail.commm)
        # NoAnswer = Domain exists but has no mail server
        raise ValidationError(f"The domain '@{domain}' does not exist or cannot receive emails.")
    except Exception as e:
        # Fallback for other errors (e.g., no internet)
        pass