import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { AcademicService } from '../core/academic/academic.service';
import { StudentOverview } from '../core/academic/academic.models';
import { AuthService } from '../core/auth/auth.service';
import { SemesterFormComponent } from './semester-form';
import { TutoringFormComponent } from './tutoring-form';
import { TutoringAgreementsComponent, ResponsibleOption } from './tutoring-agreements';
import { EvidenceUploadComponent } from './evidence-upload';

@Component({
  selector: 'app-student-overview',
  imports: [CommonModule, RouterLink, SemesterFormComponent, TutoringFormComponent, TutoringAgreementsComponent, EvidenceUploadComponent],
  templateUrl: './student-overview.html',
  styleUrl: './student-overview.scss',
})
export class StudentOverviewComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly academicService = inject(AcademicService);
  protected readonly auth = inject(AuthService);
  protected studentId = 0;
  protected overview: StudentOverview | null = null;
  protected cargando = true;
  protected error = '';
  protected mostrarFormSemestre = false;
  protected mostrarFormTutoria = false;
  protected exitoTutoria = '';

  ngOnInit(): void {
    this.studentId = Number(this.route.snapshot.paramMap.get('id'));
    if (Number.isInteger(this.studentId) && this.studentId > 0) this.cargarExpediente();
    else { this.error = 'Identificador de estudiante inválido.'; this.cargando = false; }
  }

  cargarExpediente(): void {
    this.cargando = true; this.error = ''; this.overview = null;
    this.academicService.getStudentOverview(this.studentId).pipe(finalize(() => this.cargando = false)).subscribe({
      next: data => {
        this.overview = data;
        if (this.route.snapshot.queryParamMap?.get('accion') === 'tutoria' && this.auth.hasPermission('tutoring.create')) this.mostrarFormTutoria = true;
      },
      error: err => this.error = err.status === 404
        ? 'El expediente solicitado no existe o no tiene permisos para consultarlo.'
        : err.status === 401 || err.status === 403
          ? 'No cuenta con autorización para consultar este expediente.'
          : 'Error al cargar el expediente del estudiante.',
    });
  }

  /** Personas asociadas al seguimiento (estudiante + comité) para HU-12. */
  protected responsibleOptions(): ResponsibleOption[] {
    const overview = this.overview;
    if (!overview) return [];
    const options: ResponsibleOption[] = [];
    const seen = new Set<number>();

    const push = (id: number | null | undefined, nombre: string, etiqueta: string) => {
      if (!id || seen.has(id)) return;
      seen.add(id);
      options.push({ id, nombre_completo: nombre, etiqueta });
    };

    push(overview.student.user_id, overview.student.nombre_completo || overview.nombre_completo, 'Estudiante');
    push(overview.advisors.advisor?.id, overview.advisors.advisor?.nombre_completo ?? '', 'Asesor');
    push(overview.advisors.coadvisor?.id, overview.advisors.coadvisor?.nombre_completo ?? '', 'Coasesor');
    for (const member of overview.advisors.members ?? []) {
      push(member.id, member.nombre_completo, member.rol_comite || 'Comité');
    }
    return options;
  }

  semestreGuardado(): void { this.mostrarFormSemestre = false; this.cargarExpediente(); }
  tutoriaGuardada(): void { this.mostrarFormTutoria = false; this.exitoTutoria = 'Tutoría registrada correctamente.'; this.cargarExpediente(); }
}
