import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { signal } from '@angular/core';
import { TutoringObservationsComponent } from './tutoring-observations';
import { AcademicService } from '../core/academic/academic.service';
import { AuthService } from '../core/auth/auth.service';

describe('TutoringObservationsComponent (HU-09)', () => {
  let fixture: ComponentFixture<TutoringObservationsComponent>;
  let component: TutoringObservationsComponent;

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
            semester: 3,
            fecha_sesion: '2026-09-05',
            modalidad: 'PRESENCIAL',
            resumen: 'Revisión de protocolo',
            created_by: 2,
          },
        ],
      }),
    ),
    getSessionObservations: jasmine.createSpy('getSessionObservations').and.returnValue(
      of([
        {
          id: 1,
          session: 12,
          autor: 2,
          autor_nombre: 'Roberto Gómez',
          tema_revisado: 'Metodología',
          observaciones_detalladas: 'Ampliar el marco teórico con fuentes recientes.',
          created_at: '2026-09-14T11:30:00Z',
        },
      ]),
    ),
    createSessionObservation: jasmine.createSpy('createSessionObservation').and.returnValue(
      of({
        id: 2,
        session: 12,
        autor: 2,
        autor_nombre: 'Roberto Gómez',
        tema_revisado: 'Estado del arte',
        observaciones_detalladas: 'Incluir literatura 2024-2026 sobre el tema.',
        created_at: '2026-09-15T12:00:00Z',
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
      imports: [TutoringObservationsComponent],
      providers: [
        { provide: AcademicService, useValue: academicStub },
        { provide: AuthService, useValue: authStub },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TutoringObservationsComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('studentId', 4);
    fixture.componentRef.setInput('preferredSessionId', 12);
    fixture.detectChanges();
  });

  it('carga tutorías y muestra observaciones existentes', () => {
    const text = (fixture.nativeElement as HTMLElement).textContent || '';
    expect(academicStub.getTutoringSessions).toHaveBeenCalled();
    expect(academicStub.getSessionObservations).toHaveBeenCalledWith(12);
    expect(text).toContain('Metodología');
    expect(text).toContain('Roberto Gómez');
  });

  it('registra una nueva observación en la sesión seleccionada', () => {
    academicStub.createSessionObservation.calls.reset();
    academicStub.getSessionObservations.calls.reset();
    component['form'].setValue({
      tema_revisado: 'Estado del arte',
      observaciones_detalladas: 'Incluir literatura 2024-2026 sobre el tema.',
    });
    component['submit']();
    expect(academicStub.createSessionObservation).toHaveBeenCalledWith(12, {
      tema_revisado: 'Estado del arte',
      observaciones_detalladas: 'Incluir literatura 2024-2026 sobre el tema.',
    });
    expect(academicStub.getSessionObservations).toHaveBeenCalled();
  });
});
