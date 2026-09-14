import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { finalize } from 'rxjs';
import { AcademicService } from '../core/academic/academic.service';
import { StudentOverview, Semester } from '../core/academic/academic.models';
import { AuthService } from '../core/auth/auth.service';

@Component({
  selector: 'app-student-overview',
  imports: [CommonModule, RouterLink, ReactiveFormsModule],
  templateUrl: './student-overview.html',
  styleUrl: './student-overview.scss',
})
export class StudentOverviewComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly academicService = inject(AcademicService);
  protected readonly auth = inject(AuthService);
  private readonly fb = inject(FormBuilder);

  protected studentId = 0;
  protected overview: StudentOverview | null = null;
  protected cargando = true;
  protected error = '';

  protected guardandoSemestre = false;
  protected errorSemestre = '';
  protected mostrarFormSemestre = false;

  protected mostrarFormTutoria = false;
  protected guardandoTutoria = false;
  protected errorTutoria = '';
  protected exitoTutoria = '';

  protected readonly semForm = this.fb.nonNullable.group({
    numero: [1, [Validators.required, Validators.min(1), Validators.max(6)]],
    fecha_inicio: ['', Validators.required],
    fecha_fin: ['', Validators.required],
    is_active: [true],
  });

  protected readonly tutoriaForm = this.fb.nonNullable.group({
    semester: [0, Validators.required],
    fecha_sesion: [new Date().toISOString().split('T')[0], Validators.required],
    modalidad: ['PRESENCIAL' as 'PRESENCIAL' | 'VIRTUAL' | 'HIBRIDA', Validators.required],
    resumen: ['', Validators.required],
    proxima_reunion_fecha: [''],
    proxima_reunion_notas: [''],
  });

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      this.studentId = Number(idParam);
      this.cargarExpediente();
    } else {
      this.error = 'Identificador de estudiante inválido.';
      this.cargando = false;
    }
  }

  cargarExpediente(): void {
    this.cargando = true;
    this.error = '';
    this.academicService
      .getStudentOverview(this.studentId)
      .pipe(finalize(() => (this.cargando = false)))
      .subscribe({
        next: (data) => {
          this.overview = data;
          if (this.route.snapshot.queryParamMap?.get('accion') === 'tutoria' && this.auth.hasPermission('tutoring.create')) {
            this.abrirRegistroTutoria();
          }
        },
        error: (err) => {
          if (err.status === 404) {
            this.error = 'El expediente solicitado no existe o no tiene permisos para consultarlo.';
          } else if (err.status === 401 || err.status === 403) {
            this.error = 'No cuenta con autorización para consultar este expediente.';
          } else {
            this.error = 'Error al cargar el expediente del estudiante.';
          }
        },
      });
  }

  registrarSemestre(): void {
    if (this.semForm.invalid || this.guardandoSemestre) {
      this.semForm.markAllAsTouched();
      return;
    }
    this.guardandoSemestre = true;
    this.errorSemestre = '';
    this.academicService
      .createSemester(this.studentId, this.semForm.getRawValue())
      .pipe(finalize(() => (this.guardandoSemestre = false)))
      .subscribe({
        next: () => {
          this.mostrarFormSemestre = false;
          this.semForm.reset({ numero: 1, fecha_inicio: '', fecha_fin: '', is_active: true });
          this.cargarExpediente();
        },
        error: (err) => {
          this.errorSemestre = err.error?.numero || err.error?.fecha_fin || 'No fue posible registrar el semestre.';
        },
      });
  }

  abrirRegistroTutoria(): void {
    this.mostrarFormTutoria = true;
    this.errorTutoria = '';
    this.exitoTutoria = '';
    const currentSemId = this.overview?.current_semester?.id || (this.overview?.semesters?.[0]?.id ?? 0);
    this.tutoriaForm.patchValue({
      semester: currentSemId,
      fecha_sesion: new Date().toISOString().split('T')[0],
      modalidad: 'PRESENCIAL',
      resumen: '',
      proxima_reunion_fecha: '',
      proxima_reunion_notas: '',
    });
  }

  registrarTutoria(): void {
    if (this.tutoriaForm.invalid || this.guardandoTutoria) {
      this.tutoriaForm.markAllAsTouched();
      return;
    }
    const val = this.tutoriaForm.getRawValue();
    if (!val.semester) {
      this.errorTutoria = 'El estudiante debe contar con al menos un semestre registrado para registrar su tutoría.';
      return;
    }
    this.guardandoTutoria = true;
    this.errorTutoria = '';
    this.exitoTutoria = '';
    this.academicService
      .createTutoringSession({
        student: this.studentId,
        semester: Number(val.semester),
        fecha_sesion: val.fecha_sesion,
        modalidad: val.modalidad,
        resumen: val.resumen,
        proxima_reunion_fecha: val.proxima_reunion_fecha || undefined,
        proxima_reunion_notas: val.proxima_reunion_notas || undefined,
      })
      .pipe(finalize(() => (this.guardandoTutoria = false)))
      .subscribe({
        next: () => {
          this.exitoTutoria = 'Tutoría registrada correctamente.';
          this.mostrarFormTutoria = false;
          this.cargarExpediente();
        },
        error: (err) => {
          if (err.status === 403) {
            this.errorTutoria =
              err.error?.detail ||
              'No autorizado: únicamente el asesor, coasesor o miembros activos del comité pueden registrar tutorías para este estudiante.';
          } else {
            this.errorTutoria = err.error?.detail || err.error?.resumen?.[0] || 'Error al registrar la sesión de tutoría.';
          }
        },
      });
  }
}
