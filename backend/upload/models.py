from django.db import models
from django.contrib.auth.models import User
import uuid
from django.contrib.auth.models import AbstractUser

class UploadedFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='user_files/%Y/%m/%d/')
    original_name = models.CharField(max_length=255)
    stored_name = models.CharField(max_length=255, default=uuid.uuid4, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField()
    mime = models.CharField(max_length=100)
    is_safe = models.BooleanField(default=False)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"


# ----------------------------------------------------
# 🟦 Kullanıcı KOTA Modeli
# ----------------------------------------------------
class UserQuota(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    max_storage = models.BigIntegerField(default=50 * 1024 * 1024)  # 50 MB
    used_storage = models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} kotası"
class VirusLog(models.Model):
    ACTION_CHOICES = (
        ("UPLOAD_OK", "Temiz dosya yüklendi"),
        ("UPLOAD_INFECTED", "Virüslü dosya reddedildi"),
        ("DELETE", "Dosya silindi"),
        ("DOWNLOAD", "Dosya indirildi"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    filename = models.CharField(max_length=255)
    sha256 = models.CharField(max_length=100, null=True, blank=True)
    detected = models.BooleanField(default=False)
    result_detail = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} - {self.filename}"