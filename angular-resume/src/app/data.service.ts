import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private baseURL: string = "https://my-flask-app-ge2upkdelq-uc.a.run.app";

  constructor(private http: HttpClient) { }

  uploadFiles(formData: FormData): Observable<any> {
    return this.http.post(`${this.baseURL}/upload`, formData);
  }

  getData(): Observable<any> {
    return this.http.get(`${this.baseURL}/data`);
  }
}
