from datetime import date
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.utils import OperationalError
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIRequestFactory

from .models import AcademicCommittee, AdminAuditLog, Semester, Student, TutoringSession
from .views import StudentViewSet


class StudentRBACRelationVisibilityTests(APITestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.factory = APIRequestFactory()

        self.coordinator = self.user_model.objects.create_user(
            email='coord@test.edu', password='Password123!', role=self.user_model.Role.PROGRAM_COORDINATOR
        )
        self.admin = self.user_model.objects.create_user(
            email='admin@test.edu', password='Password123!', role=self.user_model.Role.SYSTEM_ADMIN
        )
        self.tutor_1 = self.user_model.objects.create_user(
            email='tutor1@test.edu', password='Password123!', role=self.user_model.Role.TUTOR
        )
        self.tutor_2 = self.user_model.objects.create_user(
            email='tutor2@test.edu', password='Password123!', role=self.user_model.Role.TUTOR
        )
        self.student_user_1 = self.user_model.objects.create_user(
            email='student1@test.edu', password='Password123!', role=self.user_model.Role.STUDENT
        )
        self.student_user_2 = self.user_model.objects.create_user(
            email='student2@test.edu', password='Password123!', role=self.user_model.Role.STUDENT
        )

        self.student_1 = Student.objects.create(
            user=self.student_user_1, matricula='DOC-001', nombre_completo='Estudiante Uno', cohorte='2026-A'
        )
        self.student_2 = Student.objects.create(
            user=self.student_user_2, matricula='DOC-002', nombre_completo='Estudiante Dos', cohorte='2026-A'
        )

        self.assignment = AcademicCommittee.objects.create(
            student=self.student_1,
            user=self.tutor_1,
            rol_comite=AcademicCommittee.Role.PRINCIPAL_ADVISOR,
            is_active=True,
        )

    def test_coordinator_and_admin_see_all_students(self):
        token = Token.objects.create(user=self.coordinator)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get('/api/v1/students/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)

        admin_token = Token.objects.create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        res = self.client.get('/api/v1/students/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 2)

    def test_tutor_sees_only_assigned_students(self):
        token = Token.objects.create(user=self.tutor_1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get('/api/v1/students/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], self.student_1.id)
        self.assertEqual(res.data[0]['matricula'], 'DOC-001')

    def test_unassigned_tutor_sees_empty_list(self):
        token = Token.objects.create(user=self.tutor_2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get('/api/v1/students/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_deactivated_assignment_not_visible_to_tutor(self):
        self.assignment.is_active = False
        self.assignment.save()

        token = Token.objects.create(user=self.tutor_1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get('/api/v1/students/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 0)

    def test_student_sees_only_own_record(self):
        token = Token.objects.create(user=self.student_user_1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get('/api/v1/students/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], self.student_1.id)

    def test_get_queryset_direct_filtering(self):
        view = StudentViewSet()
        req = self.factory.get('/api/v1/students/')
        req.user = self.tutor_1
        view.request = req
        qs = view.get_queryset()
        self.assertEqual(list(qs), [self.student_1])


class AuthenticationApiTests(APITestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.password = 'Correcta-12345'
        self.user = self.user_model.objects.create_user(
            email='alumno@example.com',
            password=self.password,
            first_name='Ana',
            last_name='Lopez',
            role=self.user_model.Role.STUDENT,
        )

    def test_login_returns_token_and_minimal_user_data(self):
        response = self.client.post(
            '/api/auth/login/',
            {'email': self.user.email, 'password': self.password},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['role'], 'STUDENT')
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['grammatical_gender'], 'UNSPECIFIED')
        self.assertNotIn('password', response.data)

    def test_seed_account_uses_real_password_hash_and_rejects_former_master_password(self):
        call_command('populate_data', verbosity=0)
        seeded_user = self.user_model.objects.get(email='admin@nexus.com')

        self.assertNotEqual(seeded_user.password, 'Admin1234!')
        self.assertTrue(seeded_user.check_password('Admin1234!'))
        self.assertFalse(seeded_user.check_password('Password123!'))

        valid_response = self.client.post(
            '/api/auth/login/',
            {'email': seeded_user.email, 'password': 'Admin1234!'},
            format='json',
        )
        invalid_response = self.client.post(
            '/api/auth/login/',
            {'email': seeded_user.email, 'password': 'Password123!'},
            format='json',
        )

        self.assertEqual(valid_response.status_code, 200)
        self.assertEqual(invalid_response.status_code, 400)
        self.assertNotIn('token', invalid_response.data)

    def test_session_profile_includes_effective_permissions(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['roles'], ['STUDENT'])
        self.assertEqual(response.data['permissions'], ['records.read.own'])

    def test_only_role_manager_can_list_and_assign_roles(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        forbidden = self.client.get('/api/auth/users/')
        self.assertEqual(forbidden.status_code, 403)

        admin = self.user_model.objects.create_user(
            email='admin@example.com',
            password=self.password,
            first_name='Admin',
            last_name='Nexus',
            role=self.user_model.Role.ACADEMIC_ADMIN,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=admin).key}')
        listed = self.client.get('/api/auth/users/')
        self.assertEqual(listed.status_code, 200)
        updated = self.client.patch(
            f'/api/auth/users/{self.user.id}/role/',
            {'role': self.user_model.Role.TUTOR},
            format='json',
        )

        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.data['role'], 'TUTOR')
        self.assertEqual(updated.data['permissions'], ['records.read.assigned', 'tutoring.create'])
        audit_log = AdminAuditLog.objects.get(action=AdminAuditLog.Action.ROLE_ASSIGNED)
        self.assertEqual(audit_log.target_user_id, self.user.id)
        self.assertEqual(audit_log.details, {'previous_role': 'STUDENT', 'new_role': 'TUTOR'})

    def test_role_assignment_rolls_back_when_audit_log_fails(self):
        admin = self.user_model.objects.create_user(
            email='admin@example.com',
            password=self.password,
            first_name='Admin',
            last_name='Nexus',
            role=self.user_model.Role.ACADEMIC_ADMIN,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=admin).key}')

        with patch.object(AdminAuditLog.objects, 'create', side_effect=RuntimeError('audit unavailable')):
            with self.assertRaises(RuntimeError):
                self.client.patch(
                    f'/api/auth/users/{self.user.id}/role/',
                    {'role': self.user_model.Role.TUTOR},
                    format='json',
                )

        self.user.refresh_from_db()
        self.assertEqual(self.user.role, self.user_model.Role.STUDENT)
        self.assertEqual(AdminAuditLog.objects.count(), 0)

    def test_invalid_credentials_use_generic_error(self):
        response = self.client.post(
            '/api/auth/login/',
            {'email': self.user.email, 'password': 'incorrecta'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'][0], 'Correo o contrasena incorrectos.')

    def test_former_master_password_is_rejected_without_creating_token(self):
        response = self.client.post(
            '/api/auth/login/',
            {'email': self.user.email, 'password': 'Password123!'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('token', response.data)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_password_for_another_user_does_not_authenticate_target_user(self):
        other_password = 'Otra-Segura-456'
        self.user_model.objects.create_user(
            email='otra@example.com',
            password=other_password,
            role=self.user_model.Role.TUTOR,
        )

        response = self.client.post(
            '/api/auth/login/',
            {'email': self.user.email, 'password': other_password},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_login_remains_case_insensitive_for_email(self):
        response = self.client.post(
            '/api/auth/login/',
            {'email': self.user.email.upper(), 'password': self.password},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_former_master_password_rejects_unknown_email(self):
        response = self.client.post(
            '/api/auth/login/',
            {'email': 'unknown@example.com', 'password': 'Password123!'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn('token', response.data)

    def test_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        for password in (self.password, 'Password123!'):
            with self.subTest(password=password):
                response = self.client.post(
                    '/api/auth/login/',
                    {'email': self.user.email, 'password': password},
                    format='json',
                )

                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data['non_field_errors'][0], 'Correo o contrasena incorrectos.')
                self.assertFalse(Token.objects.filter(user=self.user).exists())

    def test_me_requires_a_valid_token(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['email'], self.user.email)

    def test_logout_revokes_token(self):
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        logout_response = self.client.post('/api/auth/logout/', {}, format='json')
        protected_response = self.client.get('/api/auth/me/')

        self.assertEqual(logout_response.status_code, 200)
        self.assertEqual(logout_response.data, {'logout': True})
        self.assertEqual(protected_response.status_code, 401)

    def test_register_creates_student_and_returns_authenticated_session(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'first_name': 'Luis',
                'last_name': 'Gomez',
                'email': 'luis@example.com',
                'password': 'Segura-12345',
                'matricula': 'DOC-001',
                'programa_doctoral': 'Doctorado en Ciencias',
                'cohorte': '2026',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['role'], 'STUDENT')
        self.assertIn('token', response.data)
        user = self.user_model.objects.get(email='luis@example.com')
        student = Student.objects.get(user=user)
        self.assertEqual(student.matricula, 'DOC-001')

    def test_register_rejects_duplicate_email_and_matricula(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'first_name': 'Otra',
                'last_name': 'Persona',
                'email': self.user.email,
                'password': 'Segura-12345',
                'matricula': 'DOC-001',
                'programa_doctoral': 'Doctorado en Ciencias',
                'cohorte': '2026',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)

    def test_non_student_users_do_not_require_student_profile(self):
        roles = [
            self.user_model.Role.PROGRAM_COORDINATOR,
            self.user_model.Role.TUTOR,
            self.user_model.Role.SYSTEM_ADMIN,
            self.user_model.Role.ACADEMIC_ADMIN,
        ]
        for role in roles:
            u = self.user_model.objects.create_user(
                email=f'{role.lower()}@nexus.test', password='Password123!', role=role
            )
            self.assertIsNone(u.student)
            token = Token.objects.create(user=u)
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
            response = self.client.get('/api/auth/me/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['role'], role)
            self.assertIsNone(response.data['student_id'])


class ScopeAuthorizationApiTests(APITestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.student_user = self.user_model.objects.create_user(
            email='student@example.com', password='Correcta-12345', first_name='Ana', last_name='Lopez',
            role=self.user_model.Role.STUDENT,
        )
        self.other_student_user = self.user_model.objects.create_user(
            email='other@example.com', password='Correcta-12345', first_name='Luis', last_name='Gomez',
            role=self.user_model.Role.STUDENT,
        )
        self.tutor = self.user_model.objects.create_user(
            email='tutor@example.com', password='Correcta-12345', first_name='Eva', last_name='Diaz',
            role=self.user_model.Role.TUTOR,
        )
        self.coordinator = self.user_model.objects.create_user(
            email='coordinator@example.com', password='Correcta-12345', first_name='Celia', last_name='Ruiz',
            role=self.user_model.Role.PROGRAM_COORDINATOR,
        )
        self.student = Student.objects.create(
            user=self.student_user,
            matricula='DOC-001',
            nombre_completo='Ana Lopez',
            cohorte='2026',
        )
        self.other_student = Student.objects.create(
            user=self.other_student_user,
            matricula='DOC-002',
            nombre_completo='Luis Gomez',
            cohorte='2026',
        )
        self.semester = Semester.objects.create(
            student=self.student,
            numero=1,
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 6, 30),
        )
        self.other_semester = Semester.objects.create(
            student=self.other_student,
            numero=1,
            fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 6, 30),
        )

    def authenticate(self, user):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=user).key}')

    def test_student_can_read_only_own_record(self):
        self.authenticate(self.student_user)
        own_response = self.client.get(f'/api/records/{self.student.id}/')
        other_response = self.client.get(f'/api/records/{self.other_student.id}/')

        self.assertEqual(own_response.status_code, 200)
        self.assertEqual(other_response.status_code, 404)

    def test_assigned_committee_member_and_coordinator_can_read_record(self):
        committee_member = self.user_model.objects.create_user(
            email='committee@example.com', password='Correcta-12345', first_name='Mia', last_name='Soto',
            role=self.user_model.Role.COMMITTEE_MEMBER,
        )
        AcademicCommittee.objects.create(
            student=self.student,
            user=committee_member,
            rol_comite=AcademicCommittee.Role.PRINCIPAL_ADVISOR,
        )

        self.authenticate(committee_member)
        self.assertEqual(self.client.get(f'/api/records/{self.student.id}/').status_code, 200)

        self.authenticate(self.coordinator)
        self.assertEqual(self.client.get(f'/api/records/{self.student.id}/').status_code, 200)

    def test_system_admin_cannot_read_student_record(self):
        admin = self.user_model.objects.create_user(
            email='admin_rec@example.com', password='Correcta-12345', first_name='Sys', last_name='Admin',
            role=self.user_model.Role.SYSTEM_ADMIN,
        )
        self.authenticate(admin)
        response = self.client.get(f'/api/records/{self.student.id}/')
        self.assertEqual(response.status_code, 403)

    def test_tutor_can_create_session_only_for_assigned_student(self):
        AcademicCommittee.objects.create(
            student=self.student,
            user=self.tutor,
            rol_comite=AcademicCommittee.Role.PRINCIPAL_ADVISOR,
        )
        self.authenticate(self.tutor)
        payload = {
            'student': self.student.id,
            'semester': self.semester.id,
            'fecha_sesion': '2026-02-15',
            'modalidad': 'VIRTUAL',
            'resumen': 'Seguimiento del avance.',
        }
        allowed = self.client.post('/api/tutoring/', payload, format='json')
        payload['student'] = self.other_student.id
        payload['semester'] = self.other_semester.id
        denied = self.client.post('/api/tutoring/', payload, format='json')

        self.assertEqual(allowed.status_code, 201)
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(TutoringSession.objects.count(), 1)

    def test_tutor_cannot_use_another_students_semester(self):
        AcademicCommittee.objects.create(
            student=self.student,
            user=self.tutor,
            rol_comite=AcademicCommittee.Role.PRINCIPAL_ADVISOR,
        )
        self.authenticate(self.tutor)
        response = self.client.post('/api/tutoring/', {
            'student': self.student.id,
            'semester': self.other_semester.id,
            'fecha_sesion': '2026-02-15',
            'modalidad': 'VIRTUAL',
            'resumen': 'Seguimiento.',
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TutoringSession.objects.count(), 0)

    def test_only_coordinator_can_read_global_academic_overview(self):
        self.authenticate(self.coordinator)
        allowed = self.client.get('/api/academic/overview/')
        self.assertEqual(allowed.status_code, 200)
        self.assertEqual(len(allowed.data), 2)

        self.authenticate(self.student_user)
        denied = self.client.get('/api/academic/overview/')
        self.assertEqual(denied.status_code, 403)


class SuperAdminApiTests(APITestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.admin = self.user_model.objects.create_superuser(
            email='system@example.com', password='Correcta-12345', first_name='System', last_name='Admin',
        )
        self.student_user = self.user_model.objects.create_user(
            email='student@example.com', password='Correcta-12345', first_name='Ana', last_name='Lopez',
        )
        self.student = Student.objects.create(
            user=self.student_user, matricula='DOC-001', nombre_completo='Ana Lopez', cohorte='2026',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.admin).key}')

    def test_system_admin_can_create_institutional_user(self):
        response = self.client.post('/api/admin/users/', {
            'first_name': 'Eva',
            'last_name': 'Diaz',
            'email': 'eva@example.com',
            'password': 'Segura-12345',
            'role': 'TUTOR',
        }, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['role'], 'TUTOR')
        self.assertTrue(self.user_model.objects.filter(email='eva@example.com', role='TUTOR').exists())
        self.assertTrue(AdminAuditLog.objects.filter(
            action=AdminAuditLog.Action.INSTITUTIONAL_USER_CREATED,
            actor=self.admin,
            target_user__email='eva@example.com',
        ).exists())

    def test_institutional_user_is_not_kept_if_audit_log_fails(self):
        with patch.object(AdminAuditLog.objects, 'create', side_effect=OperationalError('no such table: nexus_adminauditlog')):
            with self.assertRaises(OperationalError):
                self.client.post('/api/admin/users/', {
                    'first_name': 'Eva',
                    'last_name': 'Diaz',
                    'email': 'eva@example.com',
                    'password': 'Segura-12345',
                    'role': 'TUTOR',
                }, format='json')

        self.assertFalse(self.user_model.objects.filter(email='eva@example.com').exists())

    def test_coordinator_can_create_and_deactivate_committee_assignment_and_admin_is_forbidden(self):
        tutor = self.user_model.objects.create_user(
            email='tutor@example.com', password='Correcta-12345', first_name='Eva', last_name='Diaz',
            role=self.user_model.Role.TUTOR,
        )
        # System Admin is forbidden from managing committee
        admin_created = self.client.post('/api/admin/committee/', {
            'user': tutor.id,
            'student': self.student.id,
            'rol_comite': 'COASESOR',
            'is_active': True,
        }, format='json')
        self.assertEqual(admin_created.status_code, 403)

        # Program Coordinator can manage committee
        coord = self.user_model.objects.create_user(
            email='coord@example.com', password='Correcta-12345', first_name='Carlos', last_name='Coord',
            role=self.user_model.Role.PROGRAM_COORDINATOR,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=coord).key}')

        created = self.client.post('/api/admin/committee/', {
            'user': tutor.id,
            'student': self.student.id,
            'rol_comite': 'COASESOR',
            'is_active': True,
        }, format='json')

        self.assertEqual(created.status_code, 201)
        assignment_id = created.data['id']
        updated = self.client.patch(
            f'/api/admin/committee/{assignment_id}/',
            {'is_active': False},
            format='json',
        )

        self.assertEqual(updated.status_code, 200)
        self.assertFalse(updated.data['is_active'])
        self.assertEqual(
            AdminAuditLog.objects.filter(action=AdminAuditLog.Action.COMMITTEE_ASSIGNED).count(),
            1,
        )
        self.assertEqual(
            AdminAuditLog.objects.filter(action=AdminAuditLog.Action.COMMITTEE_STATUS_CHANGED).count(),
            1,
        )

    def test_non_admin_cannot_create_institutional_user_or_assignment(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.student_user).key}')
        user_response = self.client.post('/api/admin/users/', {}, format='json')
        assignment_response = self.client.get('/api/admin/committee/')

        self.assertEqual(user_response.status_code, 403)
        self.assertEqual(assignment_response.status_code, 403)

    def test_system_admin_can_read_audit_history_and_role_changes_are_recorded(self):
        response = self.client.patch(
            f'/api/auth/users/{self.student_user.id}/role/',
            {'role': self.user_model.Role.TUTOR},
            format='json',
        )
        audit_response = self.client.get('/api/admin/audit/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(audit_response.status_code, 200)
        self.assertEqual(audit_response.data[0]['action'], 'ROLE_ASSIGNED')
        self.assertEqual(audit_response.data[0]['details']['previous_role'], 'STUDENT')
        self.assertEqual(audit_response.data[0]['details']['new_role'], 'TUTOR')

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=self.student_user).key}')
        self.assertEqual(self.client.get('/api/admin/audit/').status_code, 403)

    def test_system_admin_can_list_active_students_for_assignments(self):
        inactive_student = Student.objects.create(
            matricula='DOC-999', nombre_completo='Inactivo', cohorte='2026', estatus_activo=False,
        )
        response = self.client.get('/api/admin/students/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual([student['id'] for student in response.data], [self.student.id])
        self.assertNotIn(inactive_student.id, [student['id'] for student in response.data])

    def test_hu05_create_semester_success(self):
        coordinator = self.user_model.objects.create_user(
            email='coord_sem@test.com', password='password123', role=self.user_model.Role.PROGRAM_COORDINATOR
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=coordinator).key}')
        payload = {
            'numero': 1,
            'fecha_inicio': '2025-01-15',
            'fecha_fin': '2025-06-30',
            'is_active': True,
        }
        response = self.client.post(f'/api/students/{self.student.id}/semesters/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['numero'], 1)
        self.assertEqual(response.data['student'], self.student.id)
        self.assertTrue(response.data['is_active'])

    def test_hu05_semester_number_out_of_range_rejected(self):
        coordinator = self.user_model.objects.create_user(
            email='coord_sem_range@test.com', password='password123', role=self.user_model.Role.PROGRAM_COORDINATOR
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=coordinator).key}')
        payload = {
            'numero': 7,
            'fecha_inicio': '2025-01-15',
            'fecha_fin': '2025-06-30',
        }
        response = self.client.post(f'/api/students/{self.student.id}/semesters/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('numero', response.data)

    def test_hu05_semester_end_date_before_start_rejected(self):
        coordinator = self.user_model.objects.create_user(
            email='coord_sem_date@test.com', password='password123', role=self.user_model.Role.PROGRAM_COORDINATOR
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=coordinator).key}')
        payload = {
            'numero': 2,
            'fecha_inicio': '2025-06-30',
            'fecha_fin': '2025-01-15',
        }
        response = self.client.post(f'/api/students/{self.student.id}/semesters/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('fecha_fin', response.data)

    def test_hu05_semester_duplicate_rejected(self):
        Semester.objects.create(
            student=self.student, numero=1, fecha_inicio='2025-01-15', fecha_fin='2025-06-30'
        )
        coordinator = self.user_model.objects.create_user(
            email='coord_sem_dup@test.com', password='password123', role=self.user_model.Role.PROGRAM_COORDINATOR
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=coordinator).key}')
        payload = {
            'numero': 1,
            'fecha_inicio': '2025-01-15',
            'fecha_fin': '2025-06-30',
        }
        response = self.client.post(f'/api/students/{self.student.id}/semesters/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('numero', response.data)

    def test_hu05_unauthorized_user_cannot_create_semester(self):
        student_user = self.user_model.objects.create_user(
            email='estudiante_sem@test.com', password='password123', role=self.user_model.Role.STUDENT
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=student_user).key}')
        payload = {
            'numero': 1,
            'fecha_inicio': '2025-01-15',
            'fecha_fin': '2025-06-30',
        }
        response = self.client.post(f'/api/students/{self.student.id}/semesters/', payload, format='json')
        self.assertEqual(response.status_code, 403)

    def test_hu06_student_overview_contains_all_six_categories(self):
        coordinator = self.user_model.objects.create_user(
            email='coord_hu06@test.com', password='password123', role=self.user_model.Role.PROGRAM_COORDINATOR
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=coordinator).key}')
        response = self.client.get(f'/api/records/{self.student.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertIn('student', data)
        self.assertIn('current_semester', data)
        self.assertIn('advisors', data)
        self.assertIn('last_tutoring', data)
        self.assertIn('open_agreements', data)
        self.assertIn('thesis_progress', data)

    def test_single_admin_restriction_cannot_promote_to_system_admin(self):
        admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        response = self.client.patch(
            f'/api/auth/users/{self.student_user.id}/role/',
            {'role': 'SYSTEM_ADMIN'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_system_admin_role_cannot_be_modified(self):
        admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        response = self.client.patch(
            f'/api/auth/users/{self.admin.id}/role/',
            {'role': 'PROGRAM_COORDINATOR'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_form_validation_name_letters_only(self):
        coord = self.user_model.objects.create_user(
            email='coord_val@test.com', password='password123', role=self.user_model.Role.PROGRAM_COORDINATOR
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=coord).key}')
        response = self.client.post('/api/coordinator/students/', {
            'first_name': 'Juan123',
            'last_name': 'Perez',
            'email': 'juan123@example.com',
            'password': 'Password-1234',
            'matricula': 'DOC202401',
            'programa_doctoral': 'Doctorado en Ciencias',
            'fecha_ingreso': '2024-01-01',
            'cohorte': '2024-A',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.data)

    def test_form_validation_matricula_max_9_chars(self):
        coord = self.user_model.objects.create_user(
            email='coord_val2@test.com', password='password123', role=self.user_model.Role.PROGRAM_COORDINATOR
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=coord).key}')
        response = self.client.post('/api/coordinator/students/', {
            'first_name': 'Juan',
            'last_name': 'Perez',
            'email': 'juanval2@example.com',
            'password': 'Password-1234',
            'matricula': '1234567890',  # 10 chars -> exceeds 9
            'programa_doctoral': 'Doctorado en Ciencias',
            'fecha_ingreso': '2024-01-01',
            'cohorte': '2024-A',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('matricula', response.data)

    def test_committee_assignment_requires_student_role_for_student(self):
        coord = self.user_model.objects.create_user(
            email='coord_com@test.com', password='password123', role=self.user_model.Role.PROGRAM_COORDINATOR
        )
        tutor = self.user_model.objects.create_user(
            email='tutor_com@test.com', password='password123', role=self.user_model.Role.TUTOR
        )
        # Create non-student user who has a student profile
        teacher_user = self.user_model.objects.create_user(
            email='prof@test.com', password='password123', role=self.user_model.Role.TUTOR
        )
        fake_student = Student.objects.create(
            user=teacher_user, matricula='FAKESTUD1', nombre_completo='Prof Fake'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=coord).key}')
        response = self.client.post('/api/admin/committee/', {
            'user': tutor.id,
            'student': fake_student.id,
            'rol_comite': 'ASESOR_PRINCIPAL',
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('student', response.data)

    def test_tutoring_unassigned_tutor_gets_403(self):
        unassigned_tutor = self.user_model.objects.create_user(
            email='unassigned@test.com', password='password123', role=self.user_model.Role.TUTOR
        )
        sem = Semester.objects.create(
            student=self.student, numero=1, fecha_inicio='2025-01-15', fecha_fin='2025-06-30'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=unassigned_tutor).key}')
        response = self.client.post('/api/tutoring/', {
            'student': self.student.id,
            'semester': sem.id,
            'fecha_sesion': '2025-02-01',
            'modalidad': 'PRESENCIAL',
            'resumen': 'Sesion no autorizada',
        }, format='json')
        self.assertEqual(response.status_code, 403)

    def test_tutoring_assigned_committee_member_gets_201(self):
        assigned_tutor = self.user_model.objects.create_user(
            email='assigned@test.com', password='password123', role=self.user_model.Role.TUTOR
        )
        AcademicCommittee.objects.create(
            student=self.student,
            user=assigned_tutor,
            rol_comite=AcademicCommittee.Role.COMMITTEE_MEMBER,
            is_active=True,
        )
        sem = Semester.objects.create(
            student=self.student, numero=1, fecha_inicio='2025-01-15', fecha_fin='2025-06-30'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=assigned_tutor).key}')
        response = self.client.post('/api/tutoring/', {
            'student': self.student.id,
            'semester': sem.id,
            'fecha_sesion': '2025-02-01',
            'modalidad': 'PRESENCIAL',
            'resumen': 'Sesion autorizada',
        }, format='json')
        self.assertEqual(response.status_code, 201)

    def test_hu06_academic_summary_canonical_endpoint(self):
        coord = self.user_model.objects.create_user(
            email='coord_hu06_sum@test.com', password='password123', role=self.user_model.Role.PROGRAM_COORDINATOR
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {Token.objects.create(user=coord).key}')
        res1 = self.client.get(f'/api/students/{self.student.id}/academic-summary/')
        self.assertEqual(res1.status_code, 200)
        res2 = self.client.get(f'/api/v1/students/{self.student.id}/overview/')
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res1.data['student']['matricula'], self.student.matricula)

    def test_non_student_user_cannot_be_changed_to_student(self):
        tutor = self.user_model.objects.create_user(
            email='tutor_role_change@test.com', password='password123', role=self.user_model.Role.TUTOR
        )
        admin_token, _ = Token.objects.get_or_create(user=self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        response = self.client.patch(
            f'/api/auth/users/{tutor.id}/role/',
            {'role': 'STUDENT'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('estudiante', response.data['detail'])

    def test_system_admin_cannot_access_academic_summary(self):
        res = self.client.get(f'/api/students/{self.student.id}/academic-summary/')
        self.assertEqual(res.status_code, 403)

    def test_user_serializer_and_registration_support_grammatical_gender(self):
        response = self.client.post(
            '/api/auth/register/',
            {
                'first_name': 'Valeria',
                'last_name': 'Rios',
                'email': 'valeria@example.com',
                'password': 'Segura-12345',
                'matricula': 'DOC-099',
                'programa_doctoral': 'Doctorado en Ciencias',
                'cohorte': '2026',
                'grammatical_gender': 'FEMININE',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['grammatical_gender'], 'FEMININE')

        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        me_response = self.client.get('/api/auth/me/')
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data['grammatical_gender'], 'FEMININE')


