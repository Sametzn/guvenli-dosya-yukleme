
from django.http import JsonResponse

def home(request):
    return JsonResponse({"message": "Backend çalışıyor!", "status": "ok"})
