from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Sum
from uploads.models import UploadedFile  # kendi modeline göre güncelle
from .models import VirusLog
from django.contrib import admin


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """Tüm kullanıcıların dosya istatistiklerini ve seviyelerini döndürür."""
    users_data = []

    for user in User.objects.all().order_by('username'):
        files = UploadedFile.objects.filter(owner=user)
        total_files = files.count()
        total_size = files.aggregate(Sum('file_size'))['file_size__sum'] or 0
        last_upload = files.order_by('-uploaded_at').first()

        # Kullanıcı seviyesini belirle
        if user.is_superuser:
            level = "Süper Admin"
        elif user.is_staff:
            level = "Admin"
        else:
            level = "Kullanıcı"

        users_data.append({
            'id': user.id,
            'username': user.username,
            'level': level,
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'last_upload': last_upload.uploaded_at.strftime("%Y-%m-%d %H:%M") if last_upload else None
        })

    # Giriş yapan kullanıcının seviyesi
    current_user = request.user
    if current_user.is_superuser:
        current_level = "Süper Admin"
    elif current_user.is_staff:
        current_level = "Admin"
    else:
        current_level = "Kullanıcı"

    return Response({
        'users': users_data,
        'current_user_level': current_level
    })
@admin.register(VirusLog)
class VirusLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'filename', 'sha256', 'detected', 'created_at')
    list_filter = ('action', 'detected', 'user')
    search_fields = ('filename', 'user__username', 'sha256')
