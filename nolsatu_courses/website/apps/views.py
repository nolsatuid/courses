from django.shortcuts import render


def privacy_policy(request):
    return render(request, 'apps/privacy_policy.html')
