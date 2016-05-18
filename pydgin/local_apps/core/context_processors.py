''' Context processors that are used to populate the context
when a template is rendered with a request'''
from django.conf import settings


def cdn(request):
    ''' Add available CDNs. '''
    return {'CDN': settings.CDN}


def appname(request):
    ''' Add app name. '''
    try:
        return {'appname': request.path.split('/')[1]}
    except Exception as e:
        print(e.message)


def recaptcha(request):
    ''' Recaptcha for contact form. '''
    try:
        return {'RECAPTCHA_KEY': settings.RECAPTCHA_KEY}
    except Exception as e:
        print(e.message)
