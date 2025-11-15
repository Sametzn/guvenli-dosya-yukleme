from django.urls import path
from .views import (
    register,
    login_user,
    upload_file,
    list_files,
    download_file,
    delete_file,
    user_stats,

    # ADMIN İşlemleri
    admin_list_users,
    admin_create_user,
    admin_delete_user,
    admin_download_user_file,
    admin_user_stats,
    promote_user,
    demote_user,
    update_quota,
    virus_logs,

    # Dosya yönetimi (Admin)
    admin_list_user_files,
    admin_delete_user_file,
)

urlpatterns = [
    # Kullanıcı işlemleri
    path('register/', register),
    path('login/', login_user),
    path('upload/', upload_file),
    path('list_files/', list_files),
    path('download/<int:file_id>/', download_file),
    path('delete/<int:file_id>/', delete_file),
    path('user_stats/', user_stats),
    path('api/virus_logs/', virus_logs),


    # ADMIN işlemleri
    path('admin/list_users/', admin_list_users),
    path('admin/create-user/', admin_create_user),
    path('admin/user-stats/', admin_user_stats),
    path('admin/delete-user/<int:user_id>/', admin_delete_user),
    path('admin/promote-user/<int:user_id>/', promote_user),
    path('admin/demote-user/<int:user_id>/', demote_user),
    path('admin/update-quota/<int:user_id>/', update_quota),

    # ADMIN dosya işlemleri
    path('admin/list_user_files/<int:user_id>/', admin_list_user_files),
    path('admin/delete_user_file/<int:file_id>/', admin_delete_user_file),
    path('admin/download_user_file/<int:file_id>/', admin_download_user_file),


]
