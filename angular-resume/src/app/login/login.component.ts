// Update in src/app/login/login.component.ts
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service'; // Import AuthService

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent {
  username: string = '';
  password: string = '';

  constructor(private authService: AuthService, private router: Router) {} // Inject AuthService and Router

  login() {
    if (this.authService.login(this.username, this.password)) {
      this.router.navigate(['/dashboard']); // Redirect to dashboard
    } else {
      alert('Invalid login');
    }
  }
}
