from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.http import FileResponse, Http404
from django.db.models import Sum
from django.contrib.auth import authenticate
from .models import UploadedFile, UserQuota
from django.http import FileResponse
import magic
from upload.utils import scan_file_with_virustotal
from .serializers import VirusLogSerializer
import os
import magic
import upload.utils as vtutils   # ✔ PATCH UYUMLU
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from upload.models import UploadedFile, UserQuota, VirusLog
from upload.utils import get_sha256  # bu kalabilir



def get_sha256(scan_result):
    if isinstance(scan_result, dict):
        return scan_result.get("meta", {}).get("file_info", {}).get("sha256")
    return None
# ======================================================
#  LOGIN
# ======================================================
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"message": "Kullanıcı adı veya şifre hatalı."}, status=401)

    token, _ = Token.objects.get_or_create(user=user)

    if user.is_superuser:
        level = "Süper Admin"
    elif user.is_staff:
        level = "Admin"
    else:
        level = "Kullanıcı"

    return Response({
        "message": "Giriş başarılı!",
        "token": token.key,
        "user_level": level,
        "user_id": user.id
    })


# ======================================================
#  REGISTER
# ======================================================
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({"message": "Kullanıcı adı ve şifre gerekli."}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"message": "Bu kullanıcı zaten var."}, status=400)

    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"message": "Kayıt başarılı!", "token": token.key})


# ======================================================
#  USER STATS (ÇAKIŞMASIZ TEK DOĞRU HAL)
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    qs = UploadedFile.objects.filter(user=request.user)
    total_size = qs.aggregate(total=Sum('size'))['total'] or 0

    quota, _ = UserQuota.objects.get_or_create(
        user=request.user,
        defaults={
            "used_storage": total_size,
            "max_storage": 50 * 1024 * 1024
        }
    )

    return Response({
        "max_storage_mb": round(quota.max_storage / 1024 / 1024, 2),
        "used_storage_mb": round(quota.used_storage / 1024 / 1024, 2),
        "remaining_mb": round((quota.max_storage - quota.used_storage) / 1024 / 1024, 2)
    })


# ======================================================
#  UPLOAD FILE
# ======================================================



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_file(request):

    quota, _ = UserQuota.objects.get_or_create(user=request.user)

    file = request.FILES.get("file")
    if not file:
        return Response({"message": "Dosya seçilmedi."}, status=400)

    # KOTA KONTROLÜ
    remaining = quota.max_storage - quota.used_storage
    if file.size > remaining:
        return Response({"message": "Kota yetersiz."}, status=403)

    # BOYUT KONTROLÜ
    if file.size > 10 * 1024 * 1024:
        return Response({"message": "Dosya 10MB'dan büyük olamaz."}, status=400)

    # ❗ UZANTI ENGELLEME (Magic şaşırsa bile EXE’yi engeller)
    ext = file.name.lower()
    blocked_ext = [
        ".exe", ".bat", ".cmd", ".sh", ".js",
        ".vbs", ".msi", ".scr", ".ps1"
    ]
    if any(ext.endswith(bad) for bad in blocked_ext):
        return Response({"message": "MIME türü engellendi"}, status=400)


    # MIME TESPİTİ
    try:
        mime = magic.from_buffer(file.read(2048), mime=True)
    except:
        return Response({"message": "MIME tespiti yapılamadı."}, status=500)
    finally:
        file.seek(0)

    # ❌ YASAK MIME LİSTESİ (Hem magic hem test için)
    blocked = [
        "application/x-msdownload",    # test fonksiyonu bunu gönderiyor
        "application/x-dosexec",
        "application/x-executable",
        "application/vnd.microsoft.portable-executable",
    ]

    if mime in blocked:
        return Response({"message": f"MIME türü engellendi: {mime}"}, status=400)

    # ✔ İZİN VERİLENLER
    allowed = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/x-empty',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]
    if mime not in allowed:
        return Response({"message": f"MIME türü engellendi: {mime}"}, status=400)

    # GEÇİCİ KAYDET
    temp_path = f"temp_{file.name}"
    with open(temp_path, "wb+") as temp:
        for chunk in file.chunks():
            temp.write(chunk)

    # VIRUSTOTAL TARAMA
    infected, scan_result = vtutils.scan_file_with_virustotal(temp_path)
    os.remove(temp_path)

    # 🔥 VİRÜSLÜ
    if infected:
        VirusLog.objects.create(
            user=request.user,
            action="UPLOAD_INFECTED",
            filename=file.name,
            sha256=get_sha256(scan_result),
            detected=True,
            result_detail=str(scan_result)
        )
        return Response({
            "message": "Dosya virüslü, yüklenmedi!",
            "scan_result": scan_result
        }, status=400)

    # ✔ TEMİZ
    VirusLog.objects.create(
        user=request.user,
        action="UPLOAD_OK",
        filename=file.name,
        sha256=get_sha256(scan_result),
        detected=False,
        result_detail=str(scan_result)
    )

    # GERÇEK KAYDETME
    upload_dir = f"media/user_files/{request.user.username}"
    os.makedirs(upload_dir, exist_ok=True)

    stored_name = file.name
    path = os.path.join(upload_dir, stored_name)
    counter = 1

    while os.path.exists(path):
        name, ext2 = os.path.splitext(file.name)
        stored_name = f"{name}_{counter}{ext2}"
        path = os.path.join(upload_dir, stored_name)
        counter += 1

    with open(path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)

    UploadedFile.objects.create(
        user=request.user,
        file=f"user_files/{request.user.username}/{stored_name}",
        original_name=file.name,
        stored_name=stored_name,
        size=file.size,
        mime=mime
    )

    quota.used_storage += file.size
    quota.save()

    return Response({"message": "Dosya yüklendi."})





# ======================================================
#  LIST FILES
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_files(request):
    files = UploadedFile.objects.filter(user=request.user)
    data = [{
        "file_id": f.id,
        "original_name": f.original_name,
        "stored_name": f.stored_name,
        "size": f.size,
        "mime": f.mime,
        "uploaded_at": f.uploaded_at
    } for f in files]

    return Response({"files": data})


# ======================================================
#  DOWNLOAD FILE
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_file(request, file_id):
    try:
        f = UploadedFile.objects.get(id=file_id, user=request.user)
    except:
        return Response({"message": "Dosya bulunamadı."}, status=404)

    if not os.path.exists(f.file.path):
        raise Http404()
    VirusLog.objects.create(
        user=request.user,
        action="DOWNLOAD",
        filename=f.stored_name,
        detected=False,
        result_detail="İndirildi"
    )

    return FileResponse(open(f.file.path, "rb"))


# ======================================================
#  DELETE FILE
# ======================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request, file_id):
    try:
        f = UploadedFile.objects.get(id=file_id, user=request.user)
    except:
        return Response({"message": "Dosya yok."}, status=404)

    size = f.size
    path = f.file.path

    if os.path.exists(path):
        os.remove(path)

    f.delete()
    VirusLog.objects.create(
        user=request.user,
        action="DELETE",
        filename=f.stored_name,
        detected=False,
        result_detail="Dosya silindi"
    )
    quota = UserQuota.objects.get(user=request.user)
    quota.used_storage -= size
    quota.save()

    return Response({"message": "Dosya silindi."})


# ======================================================
#  ADMIN USER LIST  (Eksik olan eklendi!)
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_list_users(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({"message": "Yetki yok."}, status=403)

    users = User.objects.all()
    data = []

    for u in users:
        files = UploadedFile.objects.filter(user=u)
        total_size = files.aggregate(total=Sum('size'))['total'] or 0
        quota, _ = UserQuota.objects.get_or_create(
            user=u,
            defaults={"used_storage": total_size,
                      "max_storage": 50 * 1024 * 1024}
        )

        data.append({
            "id": u.id,
            "username": u.username,
            "level": "Süper Admin" if u.is_superuser else ("Admin" if u.is_staff else "Kullanıcı"),
            "total_files": files.count(),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "used_storage_mb": round(quota.used_storage / 1024 / 1024, 2),
            "max_storage_mb": round(quota.max_storage / 1024 / 1024, 2),
            "remaining_mb": round((quota.max_storage - quota.used_storage) / 1024 / 1024, 2),
        })

    return Response({"users": data})


# ======================================================
#  ADMIN FILE LIST
# ======================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_list_user_files(request, user_id):

    # Sadece Admin veya Süper Admin
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({"message": "Yetkiniz yok."}, status=403)

    files = UploadedFile.objects.filter(user_id=user_id)

    file_list = []
    for f in files:
        file_list.append({
            "id": f.id,
            "original_name": f.original_name,
            "stored_name": f.stored_name,
            "size_mb": round(f.size / 1024 / 1024, 2),
            "mime": f.mime,
            "uploaded_at": f.uploaded_at,
            "url": "/media/" + str(f.file)  # ister kullan ister sil
        })

    return Response({"files": file_list})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_download_user_file(request, file_id):

    if not request.user.is_staff and not request.user.is_superuser:
        return Response({"message": "Yetkiniz yok."}, status=403)

    try:
        file_obj = UploadedFile.objects.get(id=file_id)
    except UploadedFile.DoesNotExist:
        return Response({"message": "Dosya bulunamadı."}, status=404)

    file_path = file_obj.file.path

    if not os.path.exists(file_path):
        return Response({"message": "Dosya fiziksel olarak bulunamadı."}, status=404)

    response = FileResponse(open(file_path, "rb"))
    response["Content-Disposition"] = f'attachment; filename="{file_obj.original_name}"'
    return response

# ======================================================
#  ADMIN DELETE FILE (HATASIZ)
# ======================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_user_file(request, file_id):

    if not request.user.is_staff and not request.user.is_superuser:
        return Response({"message": "Yetkiniz yok."}, status=403)

    try:
        file_obj = UploadedFile.objects.get(id=file_id)
    except UploadedFile.DoesNotExist:
        return Response({"message": "Dosya bulunamadı."}, status=404)

    # Fiziksel dosyayı sil
    file_path = file_obj.file.path
    if os.path.exists(file_path):
        os.remove(file_path)

    # Kullanicinin kotasindan düş
    quota = UserQuota.objects.get(user=file_obj.user)
    quota.used_storage = max(0, quota.used_storage - file_obj.size)
    quota.save()

    # DB'den sil
    file_obj.delete()

    return Response({"message": "Dosya silindi."})



# Kullanıcı oluşturma (admin)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_user(request):
    actor = request.user  # işlemi yapan kullanıcı

    username = request.data.get('username')
    password = request.data.get('password')
    level = request.data.get('level', 'Kullanıcı')  # default: normal kullanıcı

    if not username or not password:
        return Response({"message": "Kullanıcı adı ve şifre gerekli."}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"message": "Bu kullanıcı zaten var."}, status=400)

    # -------------------------
    # ADMİN → sadece normal kullanıcı açabilir
    # -------------------------
    if actor.is_staff and not actor.is_superuser:
        if level != "Kullanıcı":
            return Response({"message": "Admin sadece normal kullanıcı oluşturabilir."}, status=403)

        user = User.objects.create_user(username=username, password=password)
        return Response({"message": f"{username} adlı kullanıcı oluşturuldu."})

    # -------------------------
    # SÜPER ADMİN → her seviyede kullanıcı oluşturabilir
    # -------------------------
    if actor.is_superuser:
        user = User.objects.create_user(username=username, password=password)

        if level == "Admin":
            user.is_staff = True
        elif level == "Süper Admin":
            user.is_staff = True
            user.is_superuser = True

        user.save()

        return Response({"message": f"{username} adlı {level} oluşturuldu."})

    # -------------------------
    # Normal kullanıcı → yetki yok
    # -------------------------
    return Response({"message": "Bu işlemi yapmaya yetkiniz yok."}, status=403)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def promote_user(request, user_id):
    actor = request.user

    # Kendine işlem yapamaz
    if actor.id == user_id:
        return Response({"message": "Kendi seviyenizi değiştiremezsiniz."}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"message": "Kullanıcı bulunamadı."}, status=404)

    # -------------------------
    # SÜPER ADMİN → HERKESİ YÜKSELTEBİLİR
    # -------------------------
    if actor.is_superuser:

        # Normal → Admin
        if not user.is_staff and not user.is_superuser:
            user.is_staff = True
            user.save()
            return Response({"message": f"{user.username} artık Admin."})

        # Admin → Süper Admin
        if user.is_staff and not user.is_superuser:
            user.is_superuser = True
            user.save()
            return Response({"message": f"{user.username} artık Süper Admin."})

        # Süper Admin → daha fazla yükseltilemez
        return Response({"message": f"{user.username} zaten Süper Admin."})

    # -------------------------
    # ADMİN → SINIRLI İŞLEM
    # -------------------------
    if actor.is_staff:

        if user.is_superuser:
            return Response({"message": "Admin, Süper Admin üzerinde işlem yapamaz."}, status=403)

        if not user.is_staff:
            user.is_staff = True
            user.save()
            return Response({"message": f"{user.username} artık Admin."})

        return Response({"message": "Admin, diğer adminleri Süper Admin yapamaz."}, status=403)

    return Response({"message": "Bu işlemi yapmak için yetkiniz yok."}, status=403)

# Kullanıcı seviyesini düşürme
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demote_user(request, user_id):
    actor = request.user

    # Kendine işlem yapamaz
    if actor.id == user_id:
        return Response({"message": "Kendi seviyenizi düşüremezsiniz."}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"message": "Kullanıcı bulunamadı."}, status=404)

    # -------------------------
    # SÜPER ADMİN → HERKESİ DÜŞÜREBİLİR
    # -------------------------
    if actor.is_superuser:

        # Süper Admin → Admin
        if user.is_superuser:
            user.is_superuser = False
            user.save()
            return Response({"message": f"{user.username} artık Admin."})

        # Admin → Normal kullanıcı
        if user.is_staff:
            user.is_staff = False
            user.save()
            return Response({"message": f"{user.username} artık Normal kullanıcı."})

        return Response({"message": f"{user.username} zaten Normal kullanıcı."})

    # -------------------------
    # ADMİN →
    # -------------------------
    if actor.is_staff:

        if user.is_superuser:
            return Response({"message": "Admin, Süper Admin'i düşüremez."}, status=403)

        if not user.is_staff:
            return Response({"message": f"{user.username} zaten normal kullanıcı."})

        # Admin diğer admini normal yapabilir
        user.is_staff = False
        user.save()
        return Response({"message": f"{user.username} artık Normal kullanıcı."})

    return Response({"message": "Bu işlemi yapmak için yetkiniz yok."}, status=403)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_quota(request, user_id):
    actor = request.user  # işlemi yapan kullanıcı

    try:
        quota = UserQuota.objects.get(user_id=user_id)
        target_user = quota.user
    except UserQuota.DoesNotExist:
        return Response({"message": "Kullanıcı kotası bulunamadı."}, status=404)

    # -------------------------
    # YETKİ KONTROLÜ
    # -------------------------

    # Kimse kendi kotasını değiştiremez
    if actor.id == user_id:
        return Response({"message": "Kendi kotanızı değiştiremezsiniz."}, status=403)

    # Admin → sadece normal kullanıcıların kotasını değiştirebilir
    if actor.is_staff and not actor.is_superuser:
        if target_user.is_superuser or target_user.is_staff:
            return Response({"message": "Admin, başka adminlerin kotasını değiştiremez."}, status=403)

    # Kullanıcı → yetki yok
    if not actor.is_staff and not actor.is_superuser:
        return Response({"message": "Bu işlemi yapmaya yetkiniz yok."}, status=403)

    # -------------------------
    # KOTA GÜNCELLEME
    # -------------------------

    new_limit_mb = request.data.get("new_limit_mb")

    if new_limit_mb is None:
        return Response({"message": "Yeni kota değeri belirtilmedi."}, status=400)

    try:
        new_limit = int(new_limit_mb) * 1024 * 1024  # MB → Byte
    except:
        return Response({"message": "Kota sayısal olmalıdır."}, status=400)

    if new_limit < quota.used_storage:
        return Response({"message": "Yeni kota mevcut kullanımın altında olamaz."}, status=400)

    quota.max_storage = new_limit
    quota.save()

    return Response({
        "message": "Kullanıcının kotası güncellendi.",
        "new_limit_mb": new_limit_mb
    })

# Kullanıcı silme (admin)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_user(request, user_id):
    actor = request.user  # işlemi yapan

    # ❌ Kimse kendini silemez
    if actor.id == user_id:
        return Response({"message": "Kendinizi silemezsiniz."}, status=403)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"message": "Kullanıcı bulunamadı."}, status=404)

    # -------------------------
    # SÜPER ADMİN → herkes üzerinde işlem yapabilir
    # KENDİSİ dışındaki tüm süper adminleri de silebilir ✔
    # -------------------------
    if actor.is_superuser:
        user.delete()
        return Response({"message": f'{user.username} başarıyla silindi.'})

    # -------------------------
    # ADMİN → Süper Admin hariç herkesi silebilir
    # -------------------------
    if actor.is_staff:

        # Admin süper admini asla silemez
        if user.is_superuser:
            return Response({"message": "Admin, Süper Admin'i silemez."}, status=403)

        user.delete()
        return Response({"message": f'{user.username} başarıyla silindi.'})

    # -------------------------
    # Normal kullanıcı → hiçbir silme işlemi yapamaz
    # -------------------------
    return Response({"message": "Bu işlemi yapmaya yetkiniz yok."}, status=403)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_user_stats(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return Response({"message": "Yetkiniz yok."}, status=403)

    users = User.objects.all()
    data = []

    for u in users:
        files = UploadedFile.objects.filter(user=u)
        total_size = files.aggregate(total=Sum('size'))['total'] or 0
        quota, _ = UserQuota.objects.get_or_create(
            user=u,
            defaults={"used_storage": total_size, "max_storage": 50 * 1024 * 1024}
        )

        data.append({
            "id": u.id,
            "username": u.username,
            "level": "Süper Admin" if u.is_superuser
                     else ("Admin" if u.is_staff else "Kullanıcı"),
            "total_files": files.count(),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "used_storage_mb": round(quota.used_storage / 1024 / 1024, 2),
            "max_storage_mb": round(quota.max_storage / 1024 / 1024, 2),
            "remaining_mb": round((quota.max_storage - quota.used_storage) / 1024 / 1024, 2)
        })

    return Response({
        "users": data,
        "current_user_id": request.user.id,
        "current_user_level": (
            "Süper Admin" if request.user.is_superuser
            else ("Admin" if request.user.is_staff else "Kullanıcı")
        )
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def virus_logs(request):
    if not request.user.is_superuser:  # Yalnızca admin görebilsin
        return Response({"message": "Yetkisiz erişim"}, status=403)

    logs = VirusLog.objects.all().order_by('-created_at')
    return Response(VirusLogSerializer(logs, many=True).data)