import json

from django.conf import settings
from django.core.mail import send_mail
from django.http.response import HttpResponseForbidden, JsonResponse
from django.shortcuts import render
# import urllib


def index(request):
    ''' Renders a front page. '''
    return render(request, 'front_page.html', {'CDN': settings.CDN}, content_type='text/html')


def about(request):
    ''' Renders about page. '''
    return render(request, 'about.html', {'CDN': settings.CDN}, content_type='text/html')


def terms(request):
    ''' Renders T&Cs page. '''
    return render(request, 'terms.html', {'CDN': settings.CDN}, content_type='text/html')


def faq(request):
    ''' Renders about page. '''
    return render(request, 'faq.html', {'CDN': settings.CDN}, content_type='text/html')


def data_source(request):
    ''' Renders about page. '''
    return render(request, 'data_source.html', {'CDN': settings.CDN}, content_type='text/html')


def contact(request):
    ''' Contact us post. '''
    form_data = request.POST
#     CAPTCHA = form_data.get("g-recaptcha-response")
#     url = "https://www.google.com/recaptcha/api/siteverify?secret="+settings.RECAPTCHA_SECRET+"&response="+CAPTCHA
#     response = urllib.request.urlopen(url)
#     data = json.loads(response.read().decode(response.info().get_param('charset') or 'utf-8'))
#
#     if data.get('sucess') == False:
#         retJSON = {'error': 'Failed to confirm human-status. Please try again'}
#         return HttpResponseForbidden(json.dumps(retJSON))

    email = form_data.get("contact-email")
    message = ("Name : "+form_data.get("contact-name") +
               "\nE-mail : "+email+"\n\n" +
               form_data.get("contact-msg"))
    has_send = send_mail(subject="ImmunoBase Contact Us", message=message, from_email=email,
                         recipient_list=[email, settings.DEFAULT_FROM_EMAIL])

    if has_send > 0:
        retJSON = {'sucess': str(has_send) + ' Email(s) sent'}
        return JsonResponse(retJSON)

    retJSON = {'error': 'Email(s) failed to send.'}
    return HttpResponseForbidden(json.dumps(retJSON))
