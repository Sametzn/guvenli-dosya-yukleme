import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UploadService {

  private apiUrl = 'https://guvenli-dosya-yukleme.onrender.com/api';

  constructor(private http: HttpClient) {}

  // ==========================
  // DOSYA YÜKLEME
  // ==========================
  uploadFile(file: File, token: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post(`${this.apiUrl}/upload/`, formData, {
      headers: { 'Authorization': `Token ${token}` }
    });
  }

  // ==========================
  // DOSYA LİSTELEME
  // ==========================
  listFiles(token: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/list_files/`, {
      headers: { 'Authorization': `Token ${token}` }
    });
  }

  // ==========================
  // DOSYA İNDİRME
  // ==========================
  downloadFile(fileId: number, token: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/download/${fileId}/`, {
      headers: { 'Authorization': `Token ${token}` },
      responseType: 'blob'
    });
  }

  // ==========================
  // DOSYA SİLME
  // ==========================
  deleteFile(fileId: number, token: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/delete/${fileId}/`, {
      headers: { 'Authorization': `Token ${token}` }
    });
  }

  // ==========================
  // KULLANICI KOTA
  // ==========================
  getUserStats(token: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/user_stats/`, {
      headers: { 'Authorization': `Token ${token}` }
    });
  }
}
