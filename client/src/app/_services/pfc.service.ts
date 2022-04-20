import { Pfc } from './../_models/pfc';
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs/Observable';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';

@Injectable()
export class PfcService {

  constructor(private http: HttpClient) { }

  getAll() {
      return this.http.get<Pfc[]>(environment.api_url + '/api/pfc/list/');
  }

  getById(id: number) {
      return this.http.get<Pfc>(environment.api_url + '/api/pfc/detail/' + id + '/');
  }

  getByDate(id: string) {
      return this.http.get<Pfc>(environment.api_url + '/api/pfc/date/?date=' + id );
  }

  getByYear(year: number, valute: string, pfcId: any) {
      return this.http.get(environment.api_url + '/api/pfc/year/' + year + '/?unit=' + valute + '&pfc=' + pfcId);
  }

  create(pfc: Pfc) {
      return this.http.post(environment.api_url + '/api/pfc/list/', pfc);
  }

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
          xhr.open('POST', environment.api_url + '/api/pfc/upload/', true);
          xhr.setRequestHeader('Authorization', bearer);
          xhr.send(data);
      });
    }

uploadPFC(data: FormData) {
    //   console.log(data);
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.onreadystatechange = () => {
                if (xhr.readyState === 4) {
                    if (xhr.status === 201) {
                    resolve(xhr.response);
                    } else {
                    reject(xhr.response);
                    }
                }
            };
            const bearer = 'JWT ' + JSON.parse(localStorage.getItem('token'));
            xhr.open('POST', environment.api_url + '/api/pfc/upload/', true);
            xhr.setRequestHeader('Authorization', bearer);
            xhr.send(data);
        });
    }


  update(pfc: Pfc) {
      return this.http.put(environment.api_url + '/api/pfc/detail/' + pfc.id + '/', pfc);
  }

  delete(id: number) {
      return this.http.delete(environment.api_url + '/api/pfc/detail/' + id + '/');
  }

  getUnits() {
     return this.http.get(environment.api_url + '/api/pfc/units/');
  }

//   private handleError(error: Response) {
//       return Observable.throw(error.statusText);
//   }

  getPfcFirstRecorder(idPFC: number, years: any) {
    return this.http.get(environment.api_url + '/api/pfc/years/?pfc=' + idPFC + '&years=' + years);
    }

    getPfcPeakData(idPFC: number) {
        console.log(environment.api_url + '/api/pfc/peak/?pfc=' + idPFC);
        return this.http.get<any>(environment.api_url + '/api/pfc/peak/?pfc=' + idPFC);
    }
}
