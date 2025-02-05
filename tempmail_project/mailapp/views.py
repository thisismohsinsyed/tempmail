import random
import string
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import EmailAccount, EmailMessage

def generate_random_email():
    """Generate a random email address using a fixed domain."""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain = "tempmail.local"
    return f"{random_str}@{domain}"

def index(request):
    """
    The home view: If there is no temporary email in session, create one.
    Then, retrieve its inbox messages.
    """
    email_account_id = request.session.get('email_account_id')
    email_account = None
    if email_account_id:
        try:
            email_account = EmailAccount.objects.get(id=email_account_id)
        except EmailAccount.DoesNotExist:
            email_account = None

    if not email_account:
        email_address = generate_random_email()
        email_account = EmailAccount.objects.create(email_address=email_address)
        request.session['email_account_id'] = email_account.id

    messages = email_account.messages.order_by('-received_at')
    context = {
        'email_account': email_account,
        'messages': messages,
    }
    return render(request, 'mailapp/index.html', context)

@csrf_exempt
def receive_email(request):
    """
    Receive an email from Mailgun's inbound route.
    Expected POST parameters from Mailgun:
      - recipient: the email address the message was sent to
      - sender: the sender's email address
      - subject: the email's subject
      - body-plain: the plain text body of the email
    """
    if request.method == "POST":
        # Extract parameters from Mailgun's POST data
        recipient = request.POST.get('recipient')
        sender = request.POST.get('sender')
        subject = request.POST.get('subject')
        body_plain = request.POST.get('body-plain')

        # Validate that all required parameters are present
        if not all([recipient, sender, subject, body_plain]):
            return HttpResponseBadRequest("Missing one or more required parameters.")

        # Look up the EmailAccount that matches the recipient address
        try:
            email_account = EmailAccount.objects.get(email_address=recipient)
        except EmailAccount.DoesNotExist:
            return HttpResponseBadRequest("Email address does not exist.")

        # Create a new EmailMessage record with the incoming data
        EmailMessage.objects.create(
            email_account=email_account,
            sender=sender,
            subject=subject,
            body=body_plain
        )

        return JsonResponse({"status": "success"})
    return HttpResponseBadRequest("Only POST method allowed")
