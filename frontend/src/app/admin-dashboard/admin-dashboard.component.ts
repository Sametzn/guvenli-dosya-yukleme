import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Router } from '@angular/router';
import { UploadService } from '../services/upload.service';
import { AddUserDialogComponent } from './add-user-dialog.component';
import { QuotaDialogComponent } from '../quota-dialog/quota-dialog.component';
import { UserFilesDialogComponent } from '../user-files-dialog/user-files-dialog.component';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatDialogModule
  ],
  templateUrl: './admin-dashboard.component.html',
  styleUrls: ['./admin-dashboard.component.css']
})
export class AdminDashboardComponent implements OnInit {

  token = sessionStorage.getItem('token');

  displayedColumns = [
    'username',
    'level',
    'total_files',
    'total_size_mb',
    'used_storage_mb',
    'max_storage_mb',
    'remaining_mb',
    'actions'
  ];

  users: any[] = [];
  message = '';
  currentUserLevel = '';
  currentUserId = 0;

  constructor(
    private http: HttpClient,
    private dialog: MatDialog,
    private router: Router,
    private uploadService: UploadService
  ) {}

  ngOnInit() {
    this.loadUserStats();
  }

  // ======================================================
  // TÜM KULLANICI İSTATİSTİKLERİ
  // ======================================================
  loadUserStats() {
    const headers = new HttpHeaders({ 'Authorization': `Token ${this.token}` });

    this.http.get('https://guvenli-dosya-yukleme.onrender.com/api/admin/user-stats/', { headers }).subscribe({
      next: (res: any) => {
        this.users = res.users;
        this.currentUserLevel = res.current_user_level;
        this.currentUserId = res.current_user_id;
      },
      error: (err) => {
        this.message = err.error?.message || 'Veriler alınamadı.';
      }
    });
  }

  // ======================================================
  // YALNIZ KULLANICI LİSTESİ (dialog kapanınca çağrılıyor)
  // ======================================================
  loadUsers() {
    const headers = new HttpHeaders({ 'Authorization': `Token ${this.token}` });

    this.http.get('https://guvenli-dosya-yukleme.onrender.com/api/admin/list_users/', { headers })
      .subscribe((res: any) => {
        this.users = res.users;
      });
  }

  // ======================================================
  // KULLANICI EKLEME
  // ======================================================
  openAddUserDialog() {
    const dialogRef = this.dialog.open(AddUserDialogComponent);

    dialogRef.afterClosed().subscribe(result => {
      if (!result) return;

      const headers = new HttpHeaders({ 'Authorization': `Token ${this.token}` });

      this.http.post('https://guvenli-dosya-yukleme.onrender.com/api/admin/create-user/', result, { headers }).subscribe({
        next: (res: any) => {
          this.message = res.message;
          this.loadUserStats();
        },
        error: (err) => {
          this.message = err.error?.message || 'Kullanıcı eklenemedi.';
        }
      });
    });
  }
  isSuperAdmin(user: any): boolean {
  return user.level === "Süper Admin";
}
  // ======================================================
  // KOTA GÜNCELLEME
  // ======================================================
  openQuotaDialog(user: any) {
    const dialogRef = this.dialog.open(QuotaDialogComponent, {
      width: '350px',
      data: {
        id: user.id,
        username: user.username
      }
    });

    dialogRef.afterClosed().subscribe((newLimitMb: number | undefined) => {
      if (!newLimitMb) return;

      const headers = new HttpHeaders({ 'Authorization': `Token ${this.token}` });

      this.http.post(
        `https://guvenli-dosya-yukleme.onrender.com/api/admin/update-quota/${user.id}/`,
        { new_limit_mb: newLimitMb },
        { headers }
      ).subscribe({
        next: (res: any) => {
          this.message = res.message;
          this.loadUserStats();
        }
      });
    });
  }

  // ======================================================
  // SEVİYE YÜKSELTME
  // ======================================================
  promoteUser(id: number) {
    const headers = new HttpHeaders({ 'Authorization': `Token ${this.token}` });

    this.http.post(`https://guvenli-dosya-yukleme.onrender.com/api/admin/promote-user/${id}/`, {}, { headers }).subscribe({
      next: (res: any) => {
        this.message = res.message;
        this.loadUserStats();
      }
    });
  }

  // ======================================================
  // SEVİYE DÜŞÜRME
  // ======================================================
  demoteUser(id: number) {
    const headers = new HttpHeaders({ 'Authorization': `Token ${this.token}` });

    this.http.post(`https://guvenli-dosya-yukleme.onrender.com/api/admin/demote-user/${id}/`, {}, { headers }).subscribe({
      next: (res: any) => {
        this.message = res.message;
        this.loadUserStats();
      }
    });
  }

  // ======================================================
  // KULLANICI SİLME
  // ======================================================
  deleteUser(id: number) {
    if (!confirm('Bu kullanıcı silinsin mi?')) return;

    const headers = new HttpHeaders({ 'Authorization': `Token ${this.token}` });

    this.http.delete(`https://guvenli-dosya-yukleme.onrender.com/api/admin/delete-user/${id}/`, { headers }).subscribe({
      next: (res: any) => {
        this.message = res.message;
        this.loadUserStats();
      }
    });
  }

  // ======================================================
  // KULLANICININ DOSYALARINI AÇ
  // ======================================================
  openUserFiles(user: any) {
    const dialogRef = this.dialog.open(UserFilesDialogComponent, {
      width: "600px",
      data: {
        user_id: user.id,
        username: user.username
      }
    });

    dialogRef.afterClosed().subscribe(() => {
      this.loadUsers();
    });
  }
goVirusLogs() {
    const level = sessionStorage.getItem("user_level");

  if (level !== "Süper Admin") {
    alert("Bu sayfaya yalnızca Süper Admin erişebilir!");
    return;
  }
  this.router.navigate(['/virus-logs']);
}

  logout() {
    sessionStorage.clear();
    this.router.navigate(['/']);
  }
}

