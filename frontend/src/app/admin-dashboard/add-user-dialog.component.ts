import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSelectModule } from '@angular/material/select';

@Component({
  selector: 'app-add-user-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatDialogModule,
    MatSelectModule
  ],
  template: `
    <h2 mat-dialog-title>Yeni Kullanıcı Ekle</h2>
    <mat-dialog-content>

      <!-- Kullanıcı Adı -->
      <mat-form-field appearance="outline" class="w-100">
        <mat-label>Kullanıcı Adı</mat-label>
        <input matInput [(ngModel)]="username" />
      </mat-form-field>

      <!-- Şifre -->
      <mat-form-field appearance="outline" class="w-100">
        <mat-label>Şifre</mat-label>
        <input matInput [(ngModel)]="password" type="password" />
      </mat-form-field>

      <!-- Kullanıcı Seviyesi (Sadece Süper Admin görebilir) -->
      <mat-form-field appearance="outline" class="w-100" *ngIf="isSuperAdmin">
        <mat-label>Kullanıcı Seviyesi</mat-label>
        <mat-select [(ngModel)]="level">
          <mat-option value="Kullanıcı">Kullanıcı</mat-option>
          <mat-option value="Admin">Admin</mat-option>
          <mat-option value="Süper Admin">Süper Admin</mat-option>
        </mat-select>
      </mat-form-field>

    </mat-dialog-content>

    <mat-dialog-actions align="end">
      <button mat-button (click)="cancel()">İptal</button>
      <button mat-raised-button color="primary" (click)="save()">Kaydet</button>
    </mat-dialog-actions>
  `
})
export class AddUserDialogComponent {
  username = '';
  password = '';

  // Varsayılan: Admin için "Kullanıcı"
  level = 'Kullanıcı';

  // Login sırasında sessionStorage'a kaydedilen yetki:
  isSuperAdmin = sessionStorage.getItem('user_level') === 'Süper Admin';

  constructor(private dialogRef: MatDialogRef<AddUserDialogComponent>) {}

  cancel() {
    this.dialogRef.close();
  }

  save() {
    if (this.username && this.password) {
      this.dialogRef.close({
        username: this.username,
        password: this.password,
        level: this.level   // ← backend için gönderiliyor
      });
    }
  }
}
