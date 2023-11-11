from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from django.shortcuts import render, redirect
from .forms import RegisterForm

# SMTP Libraries
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from _config.utils import account_activation_token

def signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        
        if not form.is_valid():
            print(form.errors)
        
        if form.is_valid():
            # Save User Data
            user = form.save(commit=False)
            user.is_active = False

            # Authenticate User
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            authenticate(username=username, password=raw_password)

            # Send Verification Mail
            current_site = get_current_site(request)

            # Render email html/text
            message = render_to_string('common/email-body-text.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            html_message = render_to_string('common/email-body.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            mail_title = "Please Verify Your email Address"
            mail_to = user.email

            # Send mail
            status = send_mail(
                mail_title,
                message=message,
                from_email="noreply@ccskaist.site",
                recipient_list=[mail_to],
                html_message=html_message
            )

            # Save user data after mail sent successfully
            if status:
                user.save()

            return render(request, 'common/email-sent.html')
    else:
        form = RegisterForm()
    
    context = { 'form': form }
    return render(request, 'common/signup.html', context)

def terms(request):
    return render(request, 'common/terms.html')

def verify(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExsit):
        user = None
    
    print(f"user = {user}, account_checked = {account_activation_token.check_token(user, token)}")
    print(f"token check\nuser: {account_activation_token.make_token(user)}\ntoken: {token}")
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'common/verify-success.html')
    else:
        return render(request, 'common/verify-fail.html')

def profile(request, username):
    return render(request, 'error/comingsoon.html')

# Error handling

def error400(request, exception):
    return render(request, 'error/400.html', {})

def error404(request, exception):
    return render(request, 'error/404.html', {})

def error500(request):
    return render(request, 'error/500.html', {})