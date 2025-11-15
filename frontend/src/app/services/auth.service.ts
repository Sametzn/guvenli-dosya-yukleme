import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private baseUrl = 'http://127.0.0.1:8000/api/';  // Django backend adresi

  constructor(private http: HttpClient) { }

register(username: string, password: string) {
  return this.http.post('http://127.0.0.1:8000/api/register/', {
    username,
    password
  });
}

  login(userData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}login/`, userData);
  }
}
