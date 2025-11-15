import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  standalone: true,
  selector: 'app-user-files-dialog',
  templateUrl: './user-files-dialog.component.html',
  imports: [
    CommonModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule
  ]
})
export class UserFilesDialogComponent implements OnInit {

  files: any[] = [];
  username = '';
  isSuperAdmin = false;

  headers!: HttpHeaders;
  token = sessionStorage.getItem('token');

  constructor(
    private http: HttpClient,
    private dialogRef: MatDialogRef<UserFilesDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  ngOnInit(): void {

    this.headers = new HttpHeaders({
      "Authorization": `Token ${this.token}`
    });

    this.username = this.data.username;

    this.isSuperAdmin = sessionStorage.getItem('user_level') === 'Süper Admin';

    this.loadFiles();
  }

  // =========================================================
  // KULLANICI DOSYALARINI GETİR
  // =========================================================
  loadFiles() {
    this.http.get(
      `http://127.0.0.1:8000/api/admin/list_user_files/${this.data.user_id}/`,
      { headers: this.headers }
    )
    .subscribe({
      next: (res: any) => {
        this.files = res.files;
      },
      error: (err) => {
        console.error(err);
        alert("Dosyalar alınamadı!");
      }
    });
  }


downloadFile(file_id: number) {
  this.http.get(
    `http://127.0.0.1:8000/api/admin/download_user_file/${file_id}/`,
    {
      headers: this.headers,
      responseType: 'blob'
    }
  )
  .subscribe({
    next: (blob: Blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "dosya";
      a.click();
      window.URL.revokeObjectURL(url);
    },
    error: () => alert("Dosya indirilemedi!")
  });
}

  // =========================================================
  // DOSYA SİLME
  // =========================================================
  deleteFile(file_id: number) {
    if (!confirm("Bu dosya silinsin mi?")) return;

    this.http.delete(
      `http://127.0.0.1:8000/api/admin/delete_user_file/${file_id}/`,
      { headers: this.headers }
    )
    .subscribe({
      next: () => {
        this.loadFiles();
      },
      error: () => {
        alert("Dosya silinemedi!");
      }
    });
  }

  close() {
    this.dialogRef.close();
  }
}
