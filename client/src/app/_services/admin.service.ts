import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Admin } from '../_models/index';
import { Pagination } from '../_models/pagination';

@Injectable()
export class AdminService {
    constructor(private http: HttpClient) { }

    getAll(pag: number) {
        return this.http.get<Pagination<Admin>>(environment.api_url + '/api/user/client/list/' + '?pag=' + pag);
    }

    getById(pk: number) {
        return this.http.get<Admin>(environment.api_url + '/api/user/client/id/' + pk + '/');
    }

    create(client: Admin) {
        return this.http.post(environment.api_url + '/api/user/client/list/', client);
    }

    update(admin: Admin) {
        console.log(environment.api_url + '/api/user/client/id/' + admin.pk + '/', admin);
        return this.http.put(environment.api_url + '/api/user/client/id/' + admin.pk + '/', admin);
    }

    delete(pk: number) {
        return this.http.delete(environment.api_url + '/api/user/client/id/' + pk + '/');
    }

    deletePods(name: string) {
        return this.http.delete(environment.api_url + '/api/company/meter/dlname/?meter=' + name );
    }


    setPassword(admin: Admin) {
        return this.http.put(environment.api_url + '/api/user/change/pass/' + admin.pk + '/', admin.pk);
    }

    postPassword(token: any, password: any) {
        return this.http.post(environment.api_url + '/api/user/change/pass/' + 0 + '/', {'temp': token, 'password': password});
    }

    getPassword(temp: any) {
        return this.http.get(environment.api_url + '/api/user/change/pass/' + 0 + '/?temp=' + temp);
    }


    uploadFile(data: FormData, what: any, id?: number) {
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
          if (what === 'add') { xhr.open('POST', environment.api_url + '/api/user/client/list/', true); }
          if (what === 'edit') { xhr.open('PUT', environment.api_url + '/api/user/client/id/' + id + '/', true); }
          xhr.setRequestHeader('Authorization', bearer);
          xhr.send(data);
        });
      }



      verifyExistPod(meter: any) {
        return this.http.get<any>(environment.api_url + '/api/company/meter/name/?meter=' +  meter);
    }
}
