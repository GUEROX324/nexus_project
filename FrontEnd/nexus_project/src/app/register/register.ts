import { Component, inject } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink, Router } from '@angular/router';
import { finalize } from 'rxjs';
import { AuthService } from '../core/auth/auth.service';

@Component({
  selector: 'app-register',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.scss',
})
export class Register {
  private readonly formBuilder = inject(NonNullableFormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  protected readonly form = this.formBuilder.group({
    first_name: ['', [Validators.required, Validators.maxLength(150), Validators.pattern(/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/)]],
    last_name: ['', [Validators.required, Validators.maxLength(150), Validators.pattern(/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/)]],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    passwordConfirmation: ['', [Validators.required]],
    matricula: ['', [Validators.required, Validators.maxLength(9), Validators.pattern(/^[a-zA-Z0-9-]{1,9}$/)]],
    programa_doctoral: ['Doctorado en Ciencias', [Validators.required]],
    cohorte: ['', [Validators.required, Validators.maxLength(20)]],
  });
  protected isSubmitting = false;
  protected registerError = false;
  protected showPassword = false;
  protected showConfirmPassword = false;

  bloquearNumeros(event: KeyboardEvent): void {
    if (event.key >= '0' && event.key <= '9') {
      event.preventDefault();
    }
  }

  filtrarNumeros(event: Event, controlName: 'first_name' | 'last_name'): void {
    const input = event.target as HTMLInputElement;
    if (input) {
      const sanitized = input.value.replace(/[0-9]/g, '');
      if (input.value !== sanitized) {
        input.value = sanitized;
        this.form.get(controlName)?.setValue(sanitized);
      }
    }
  }

  submit(): void {
    this.registerError = false;
    if (this.form.invalid || this.form.controls.password.value !== this.form.controls.passwordConfirmation.value) {
      this.form.markAllAsTouched();
      return;
    }

    const { passwordConfirmation: _, ...registration } = this.form.getRawValue();
    this.isSubmitting = true;
    this.auth.register(registration).pipe(
      finalize(() => this.isSubmitting = false),
    ).subscribe({
      next: () => void this.router.navigate(['/home']),
      error: () => this.registerError = true,
    });
  }

  protected passwordsMatch(): boolean {
    return this.form.controls.password.value === this.form.controls.passwordConfirmation.value;
  }
}
