import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from './services/auth.service';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    RouterOutlet,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {

  username = '';
  password = '';
  message = '';

  // 🔥 Kayan Başlık İçin Değişkenler
  titleText = " Güvenli Dosya Sistemi - Hoş Geldiniz ";
  position = 0;

  constructor(private authService: AuthService, private router: Router) {}

  // 🔥 Tarayıcı Sekmesinde Kayan Yazı Başlat
  ngOnInit() {
    setInterval(() => {
      this.position++;
      if (this.position > this.titleText.length) {
        this.position = 0;
      }

      document.title =
        this.titleText.substring(this.position) +
        this.titleText.substring(0, this.position);

    }, 200); // hız (ms)
  }

  // Kullanıcı kayıt işlemi
  register() {
    this.authService.register(this.username, this.password).subscribe({
      next: (res: any) => {
        this.message = res.message;
      },
      error: (err) => {
        this.message = err.error.message;
      }
    });
  }

  // Giriş işlemi
  login() {
    this.authService.login({ username: this.username, password: this.password }).subscribe({
      next: (res: any) => {
        this.message = res.message;
        sessionStorage.setItem('token', res.token);

        if (res.is_superuser) {
          console.log('➡️ Admin yönlendirmesi');
          this.router.navigate(['/admin-dashboard']);
        } else {
          console.log('👤 Normal kullanıcı yönlendirmesi');
          this.router.navigate(['/user-dashboard']);
        }
      },
      error: (err) => {
        this.message = err.error.message;
      }
    });
  }
}
