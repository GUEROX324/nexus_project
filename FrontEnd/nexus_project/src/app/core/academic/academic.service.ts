import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { PaginatedResponse } from '../../shared/pagination';
import { StudentRecord, TutoringSession, TutoringSessionData, Semester, CreateSemesterData, StudentOverview } from './academic.models';

const API = environment.apiUrl;

@Injectable({ providedIn: 'root' })
export class AcademicService {
  constructor(private readonly http: HttpClient) {}

  getStudentRecord(studentId: number): Observable<StudentRecord> {
    return this.http.get<StudentRecord>(`${API}/students/${studentId}/overview/`);
  }

  getStudentOverview(studentId: number): Observable<StudentOverview> {
    return this.http.get<StudentOverview>(`${API}/students/${studentId}/overview/`);
  }

  createTutoringSession(data: TutoringSessionData): Observable<TutoringSession> {
    return this.http.post<TutoringSession>(`${API}/tutoring-sessions/`, data);
  }

  getGlobalOverview(page = 1): Observable<PaginatedResponse<StudentRecord>> {
    return this.http.get<PaginatedResponse<StudentRecord>>(`${API}/academic/overview/?page=${page}`);
  }

  getStudentSemesters(studentId: number): Observable<Semester[]> {
    return this.http.get<Semester[]>(`${API}/students/${studentId}/semesters/`);
  }

  createSemester(studentId: number, data: CreateSemesterData): Observable<Semester> {
    return this.http.post<Semester>(`${API}/students/${studentId}/semesters/`, data);
  }
}