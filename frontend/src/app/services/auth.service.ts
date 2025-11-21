import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private baseUrl = 'https://guvenli-dosya-yukleme.onrender.com/api/';

  constructor(private http: HttpClient) { }

  register(username: string, password: string) {
    return this.http.post(`${this.baseUrl}register/`, {
      username,
      password
    });
  }

  login(userData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}login/`, userData);
  }
}

