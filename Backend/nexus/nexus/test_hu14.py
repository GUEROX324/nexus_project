from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import (
    AcademicCommittee,
    Agreement,
    AgreementAuditLog,
    CommitteeMembership,
    Semester,
    Student,
    TutoringSession,
)
from .tests import jwt_for


class AgreementQueryHu14Tests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.u = User.objects.create_user(email='t14@x.co', password='x', role=User.Role.TUTOR)
        self.other = User.objects.create_user(email='o14@x.co', password='x', role=User.Role.TUTOR)
        self.s = Student.objects.create(matricula='HU14', nombre_completo='S', cohorte='26')
        self.hidden = Student.objects.create(matricula='H14X', nombre_completo='X', cohorte='26')
        CommitteeMembership.objects.create(
            committee=AcademicCommittee.objects.create(student=self.s),
            user=self.u,
            role='ASESOR',
        )
        today = timezone.localdate()
        self.semester = Semester.objects.create(
            student=self.s,
            numero=2,
            fecha_inicio=today - timedelta(days=90),
            fecha_fin=today + timedelta(days=90),
            is_active=True,
        )
        self.session = TutoringSession.objects.create(
            student=self.s,
            semester=self.semester,
            fecha_sesion=today - timedelta(days=10),
            modalidad=TutoringSession.Modality.VIRTUAL,
            resumen='Sesión HU-14',
            created_by=self.u,
        )
        self.a = Agreement.objects.create(
            student=self.s,
            session=self.session,
            descripcion='visible',
            responsable=self.u,
            fecha_limite=today - timedelta(days=1),
            estado='PENDIENTE',
        )
        Agreement.objects.create(
            student=self.s,
            session=self.session,
            descripcion='future',
            responsable=self.other,
            fecha_limite=today + timedelta(days=1),
            estado='PENDIENTE',
        )
        Agreement.objects.create(
            student=self.hidden,
            descripcion='hidden',
            responsable=self.u,
            fecha_limite=today - timedelta(days=1),
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {jwt_for(self.u)}')

    def test_combined_filters_pagination_and_scope(self):
        r = self.client.get(
            f'/api/v1/agreements/?student={self.s.id}&responsable={self.u.id}'
            f'&estado=PENDIENTE&vencido=true&page_size=1'
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['descripcion'], 'visible')
        self.assertEqual(r.data['results'][0]['student_nombre'], 'S')
        self.assertEqual(r.data['results'][0]['semester'], self.semester.id)

    def test_filter_by_semester_and_fecha_limite(self):
        today = timezone.localdate()
        r = self.client.get(
            f'/api/v1/agreements/?semester={self.semester.id}'
            f'&fecha_limite={today - timedelta(days=1)}'
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['descripcion'], 'visible')

    def test_filter_estado_vencido_derived(self):
        r = self.client.get('/api/v1/agreements/?estado=VENCIDO')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['count'], 1)
        self.assertEqual(r.data['results'][0]['descripcion'], 'visible')
        self.assertTrue(r.data['results'][0]['is_vencido'])

    def test_audit_log_is_read_only(self):
        AgreementAuditLog.objects.create(
            agreement=self.a,
            user=self.u,
            estado_anterior='PENDIENTE',
            estado_nuevo='EN_PROCESO',
        )
        url = f'/api/v1/agreements/{self.a.id}/audit-log/'
        self.assertEqual(len(self.client.get(url).data), 1)
        for method in ('post', 'put', 'patch', 'delete'):
            self.assertEqual(getattr(self.client, method)(url, {}, format='json').status_code, 405)
