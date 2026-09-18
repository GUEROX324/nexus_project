import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { AcademicService } from '../core/academic/academic.service';
import { Agreement, TutoringSession } from '../core/academic/academic.models';
import { AuthService } from '../core/auth/auth.service';

/** HU-11: crear y listar acuerdos asociados a una tutoría (solo descripción en UI). */
@Component({
  selector: 'app-tutoring-agreements',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './tutoring-agreements.html',
  styleUrl: './tutoring-agreements.scss',
})
export class TutoringAgreementsComponent implements OnChanges {
  @Input({ required: true }) studentId!: number;
  @Input() preferredSessionId: number | null = null;
  @Output() changed = new EventEmitter<void>();

  private readonly academic = inject(AcademicService);
  private readonly fb = inject(FormBuilder);
  protected readonly auth = inject(AuthService);

  protected sessions: TutoringSession[] = [];
  protected selectedSessionId: number | null = null;
  protected agreements: Agreement[] = [];
  protected cargando = false;
  protected guardando = false;
  protected error = '';
  protected exito = '';

  protected readonly form = this.fb.nonNullable.group({
    descripcion: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(1000)]],
  });

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['studentId'] || changes['preferredSessionId']) {
      this.cargarSesiones();
    }
  }

  protected puedeRegistrar(): boolean {
    return this.auth.hasPermission('tutoring.create');
  }

  protected onSessionChange(raw: string): void {
    const id = Number(raw);
    this.selectedSessionId = Number.isInteger(id) && id > 0 ? id : null;
    this.exito = '';
    this.error = '';
    this.cargarAcuerdos();
  }

  protected submit(): void {
    if (!this.selectedSessionId || this.form.invalid || this.guardando) {
      this.form.markAllAsTouched();
      return;
    }
    const userId = this.auth.user()?.id;
    if (!userId) {
      this.error = 'No hay usuario autenticado para registrar el acuerdo.';
      return;
    }

    this.guardando = true;
    this.error = '';
    this.exito = '';
    // HU-11: la UI solo pide descripción. responsable/fecha van por defecto (HU-12 los hará explícitos).
    this.academic
      .createSessionAgreement(this.selectedSessionId, {
        descripcion: this.form.controls.descripcion.value.trim(),
        responsable: userId,
        fecha_limite: this.defaultFechaLimite(),
      })
      .pipe(finalize(() => (this.guardando = false)))
      .subscribe({
        next: () => {
          this.form.reset({ descripcion: '' });
          this.exito = 'Acuerdo registrado correctamente.';
          this.cargarAcuerdos();
          this.changed.emit();
        },
        error: (err) => {
          this.error =
            err.error?.descripcion?.[0] ||
            err.error?.detail ||
            'No fue posible registrar el acuerdo.';
        },
      });
  }

  private defaultFechaLimite(): string {
    const d = new Date();
    d.setDate(d.getDate() + 14);
    return d.toISOString().slice(0, 10);
  }

  private cargarSesiones(): void {
    if (!this.studentId) return;
    this.cargando = true;
    this.error = '';
    this.academic
      .getTutoringSessions(1)
      .pipe(finalize(() => (this.cargando = false)))
      .subscribe({
        next: (data) => {
          this.sessions = data.results
            .filter((s) => s.student === this.studentId)
            .sort((a, b) => b.fecha_sesion.localeCompare(a.fecha_sesion) || b.id - a.id);
          const preferred = this.preferredSessionId;
          const exists = preferred != null && this.sessions.some((s) => s.id === preferred);
          this.selectedSessionId = exists ? preferred : this.sessions[0]?.id ?? null;
          this.cargarAcuerdos();
        },
        error: () => {
          this.sessions = [];
          this.agreements = [];
          this.error = 'No fue posible cargar las tutorías para acuerdos.';
        },
      });
  }

  private cargarAcuerdos(): void {
    if (!this.selectedSessionId) {
      this.agreements = [];
      return;
    }
    this.academic.getSessionAgreements(this.selectedSessionId).subscribe({
      next: (items) => (this.agreements = items),
      error: () => {
        this.agreements = [];
        this.error = 'No fue posible cargar los acuerdos de la tutoría.';
      },
    });
  }
}
