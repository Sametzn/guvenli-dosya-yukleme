import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-quota-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],
  template: `
    <h2 mat-dialog-title>Kota Güncelle</h2>

    <mat-dialog-content>
      <p><strong>{{ data.username }}</strong> kullanıcısının kotasını değiştir.</p>

      <mat-form-field appearance="outline" class="w-100">
        <mat-label>Yeni Kota (MB)</mat-label>
        <input matInput type="number" [(ngModel)]="newLimit" />
      </mat-form-field>
    </mat-dialog-content>

    <mat-dialog-actions align="end">
      <button mat-button (click)="close()">İptal</button>
      <button mat-raised-button color="primary" (click)="save()">Kaydet</button>
    </mat-dialog-actions>
  `
})
export class QuotaDialogComponent {
  newLimit = 0;

  constructor(
    private dialogRef: MatDialogRef<QuotaDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {}

  close() {
    this.dialogRef.close();
  }

  save() {
    if (this.newLimit && this.newLimit > 0) {
      this.dialogRef.close(this.newLimit);
    }
  }
}
