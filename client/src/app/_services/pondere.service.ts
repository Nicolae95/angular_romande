import { Pondere } from './../_models/pondere';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

@Injectable()
export class PondereService {

  constructor(private http: HttpClient) { }

  upload(data: FormData) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.onreadystatechange = () => {
        if (xhr.readyState === 4) {
          if (xhr.status === 200) {
            resolve(xhr.response);
          } else {
            reject(xhr.response);
          }
        }
      };
      const bearer = 'JWT ' + JSON.parse(localStorage.getItem('token'));
      xhr.open('POST', environment.api_url + '/api/pondere/upload/', true);
      xhr.setRequestHeader('Authorization', bearer);
      xhr.send(data);
    });
  }

  getAll() {
    // console.log(environment.api_url + '/api/pondere/list/');
    return this.http.get<Pondere[]>(environment.api_url + '/api/pondere/list/');
  }

  getByYear(year: number, id: number) {
    // console.log(environment.api_url + '/api/pondere/year/' + year + '/id/' + id + '/');
    return this.http.get(environment.api_url + '/api/pondere/year/' + year + '/id/' + id + '/');
  }

}
