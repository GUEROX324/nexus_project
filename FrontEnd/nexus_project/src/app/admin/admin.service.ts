import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AuthenticatedUser } from '../core/auth/auth.models';
import { AcademicCommittee, AdminAuditLog, AdminStudent, CommitteeMembership, CommitteeRole, InstitutionalUserCreate } from './admin.models';

const API = `${environment.apiUrl}/v1`;

@Injectable({ providedIn: 'root' })
export class AdminService {
  constructor(private readonly http: HttpClient) {}

  createInstitutionalUser(data: InstitutionalUserCreate): Observable<AuthenticatedUser> {
    return this.http.post<AuthenticatedUser>(`${API}/admin/users/`, data);
  }

  getUsers(): Observable<AuthenticatedUser[]> {
    return this.http.get<AuthenticatedUser[]>(`${API}/auth/users/`);
  }

  getStudents(): Observable<AdminStudent[]> {
    return this.http.get<AdminStudent[]>(`${API}/admin/students/`);
  }

  getCommittees(): Observable<AcademicCommittee[]> {
    return this.http.get<AcademicCommittee[]>(`${API}/committees/`);
  }

  createCommittee(student: number, user: number, role: CommitteeRole): Observable<AcademicCommittee> {
    return this.http.post<AcademicCommittee>(`${API}/committees/`, { student, memberships: [{ user, role }] });
  }

  deleteCommitteeMembership(id: number): Observable<void> {
    return this.http.delete<void>(`${API}/committee-memberships/${id}/`);
  }

  getAuditLogs(): Observable<AdminAuditLog[]> {
    return this.http.get<AdminAuditLog[]>(`${API}/admin/audit/`);
  }
}