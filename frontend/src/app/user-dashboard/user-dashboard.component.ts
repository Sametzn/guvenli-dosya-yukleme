import { Component, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { Router } from '@angular/router';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { UploadService } from '../services/upload.service';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-user-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatTableModule,
    MatSortModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatProgressBarModule,
    MatCheckboxModule
  ],
  templateUrl: './user-dashboard.component.html',
  styleUrls: ['./user-dashboard.component.css']
})
export class UserDashboardComponent implements OnInit {

  displayedColumns: string[] = ['select', 'original_name', 'size', 'uploaded_at', 'actions'];
  dataSource = new MatTableDataSource<any>();
  selectedFile: File | null = null;
  selectedFiles: any[] = [];
  message = '';

  quota = {
    limit: 0,
    used: 0,
    remaining: 0
  };

  token = sessionStorage.getItem('token');

  @ViewChild(MatSort) sort!: MatSort;

  constructor(
    private uploadService: UploadService,
    private http: HttpClient,
    private router: Router
  ) {}

  ngOnInit() {
    this.checkAccess();
    this.loadFiles();
    this.loadQuota();
  }

  checkAccess() {
    const role = sessionStorage.getItem('user_level');
    if (role === "Admin" || role === "Süper Admin") {
      this.router.navigate(['/admin-dashboard']);
    }
  }

loadFiles() {
  const headers = new HttpHeaders({ 'Authorization': `Token ${this.token}` });

  this.http.get('https://guvenli-dosya-yukleme.onrender.com/api/list_files/', { headers })
    .subscribe((res: any) => {
      this.dataSource.data = res.files;
      this.dataSource.sort = this.sort;
    });
}

  loadQuota() {
    const headers = new HttpHeaders({ 'Authorization': `Token ${this.token}` });

    this.http.get('https://guvenli-dosya-yukleme.onrender.com/api/user_stats/', { headers })
      .subscribe((res: any) => {
        this.quota.limit = res.max_storage_mb;
        this.quota.used = res.used_storage_mb;
        this.quota.remaining = res.remaining_mb;
      });
  }

  applyFilter(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    this.dataSource.filter = value.trim().toLowerCase();
  }

  isSelected(file: any) {
    return this.selectedFiles.includes(file);
  }

  toggleSelection(file: any) {
    if (this.isSelected(file)) this.selectedFiles = this.selectedFiles.filter(f => f !== file);
    else this.selectedFiles.push(file);
  }

  toggleAll(event: any) {
    if (event.checked) this.selectedFiles = [...this.dataSource.data];
    else this.selectedFiles = [];
  }

  isAllSelected() {
    return (
      this.selectedFiles.length === this.dataSource.data.length &&
      this.dataSource.data.length > 0
    );
  }

  async deleteSelected() {
    if (!confirm("Seçilen dosyalar silinsin mi?")) return;

    for (const file of this.selectedFiles) {
      await firstValueFrom(this.uploadService.deleteFile(file.file_id, this.token!));
    }

    this.selectedFiles = [];
    this.loadFiles();
    this.loadQuota();
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files.item(0);
  }

upload() {
  if (!this.selectedFile) {
    this.message = "Lütfen bir dosya seçin!";
    return;
  }

  this.uploadService.uploadFile(this.selectedFile, this.token!).subscribe({
    next: (res) => {
      this.message = res.message;
      this.loadFiles();
      this.loadQuota();
    },
    error: (err) => {
      console.log("Upload Error:", err);

      // 🔥 Virüs tespiti geldi mi?
      if (err.error?.virus) {
        this.message = `⚠️ Dosyada virüs tespit edildi: ${err.error.virus}`;
        alert(this.message); // (isteğe bağlı popup)
      }
      else if (err.error?.message) {
        this.message = err.error.message;
      }
      else {
        this.message = "Yükleme hatası.";
      }
    }
  });
}


  download(id: number, name: string) {
    this.uploadService.downloadFile(id, this.token!).subscribe(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = name;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  delete(id: number) {
    if (!confirm("Bu dosya silinsin mi?")) return;

    this.uploadService.deleteFile(id, this.token!).subscribe(() => {
      this.loadFiles();
      this.loadQuota();
    });
  }

  logout() {
    sessionStorage.clear();
    this.router.navigate(['/']);
  }
}
