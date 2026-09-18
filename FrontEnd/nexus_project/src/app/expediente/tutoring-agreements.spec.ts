import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { signal } from '@angular/core';
import { TutoringAgreementsComponent } from './tutoring-agreements';
import { AcademicService } from '../core/academic/academic.service';
import { AuthService } from '../core/auth/auth.service';

describe('TutoringAgreementsComponent (HU-11)', () => {
  let fixture: ComponentFixture<TutoringAgreementsComponent>;
  let component: TutoringAgreementsComponent;

  const academicStub = {
    getTutoringSessions: jasmine.createSpy('getTutoringSessions').and.returnValue(
      of({
        count: 1,
        next: null,
        previous: null,
        results: [
          {
            id: 12,
            student: 4,
            semester: 1,
            fecha_sesion: '2026-09-05',
            modalidad: 'PRESENCIAL',
            resumen: 'Avance',
            created_by: 2,
          },
        ],
      }),
    ),
    getSessionAgreements: jasmine.createSpy('getSessionAgreements').and.returnValue(
      of([
        {
          id: 85,
          student: 4,
          session: 12,
          descripcion: 'Entregar capítulo 3 preliminar completo.',
          responsable: 2,
          responsable_nombre: 'Roberto Gómez',
          fecha_limite: '2026-09-30',
          estado: 'PENDIENTE' as const,
          is_vencido: false,
        },
      ]),
    ),
    createSessionAgreement: jasmine.createSpy('createSessionAgreement').and.returnValue(
      of({
        id: 86,
        student: 4,
        session: 12,
        descripcion: 'Nueva tarea de seguimiento académico.',
        responsable: 2,
        responsable_nombre: 'Roberto Gómez',
        fecha_limite: '2026-10-15',
        estado: 'PENDIENTE' as const,
        is_vencido: false,
      }),
    ),
  };

  const authStub = {
    user: signal({
      id: 2,
      email: 'roberto.gomez@nexus.edu',
      first_name: 'Roberto',
      last_name: 'Gómez',
      role: 'TUTOR',
      roles: ['TUTOR'],
      permissions: ['tutoring.create', 'records.read.assigned'],
    }),
    hasPermission: (p: string) => p === 'tutoring.create' || p === 'records.read.assigned',
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TutoringAgreementsComponent],
      providers: [
        { provide: AcademicService, useValue: academicStub },
        { provide: AuthService, useValue: authStub },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TutoringAgreementsComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('studentId', 4);
    fixture.componentRef.setInput('preferredSessionId', 12);
    fixture.detectChanges();
  });

  it('lista acuerdos de la tutoría (HU-11)', () => {
    const text = (fixture.nativeElement as HTMLElement).textContent || '';
    expect(academicStub.getSessionAgreements).toHaveBeenCalledWith(12);
    expect(text).toContain('Entregar capítulo 3 preliminar completo.');
    expect(text).toContain('PENDIENTE');
  });

  it('crea acuerdo asociado a la tutoría (HU-11)', () => {
    academicStub.createSessionAgreement.calls.reset();
    component['form'].setValue({
      descripcion: 'Nueva tarea de seguimiento académico.',
    });
    component['submit']();
    expect(academicStub.createSessionAgreement).toHaveBeenCalled();
    const [sessionId, payload] = academicStub.createSessionAgreement.calls.mostRecent().args;
    expect(sessionId).toBe(12);
    expect(payload.descripcion).toBe('Nueva tarea de seguimiento académico.');
    expect(payload.responsable).toBe(2);
    expect(payload.fecha_limite).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });
});
