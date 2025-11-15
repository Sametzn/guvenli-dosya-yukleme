import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCardModule } from '@angular/material/card';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatCardModule
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {

  username = '';
  password = '';
  message = '';

  constructor(
    private http: HttpClient,
    private authService: AuthService,
    private router: Router
  ) {}

  login() {
    const data = { username: this.username, password: this.password };

    this.http.post('http://127.0.0.1:8000/api/login/', data).subscribe({
      next: (res: any) => {
        sessionStorage.setItem('token', res.token);
        sessionStorage.setItem('user_level', res.user_level);
        sessionStorage.setItem('user_id', res.user_id);

        if (res.user_level === "Süper Admin" || res.user_level === "Admin") {
          this.router.navigate(['/admin-dashboard']);
        } else {
          this.router.navigate(['/user-dashboard']);
        }
      },
      error: () => {
        this.message = "Giriş başarısız.";
      }
    });
  }

  register() {
    this.authService.register(this.username, this.password).subscribe({
      next: (res: any) => {
        this.message = res.message || "Kayıt başarılı!";
      },
      error: (err) => {
        this.message = err.error?.message || "Kayıt başarısız.";
      }
    });
  }
}
