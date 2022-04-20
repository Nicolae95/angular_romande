
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable()
export class DashboardService {
    constructor(private http: HttpClient) { }

    getDashboard(id: number, year: number) {
        return this.http.get<any>(environment.api_url + '/api/company/dashboard/' + id + '/?year=' + year);
    }

}
