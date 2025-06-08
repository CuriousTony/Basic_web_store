from django.shortcuts import render


def analytics(request):
    return render(request, 'analytics/analytics.html')
