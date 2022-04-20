import { Pfc } from '../_models/pfc';
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs/Observable';
import { Subject } from 'rxjs/Subject';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { BehaviorSubject } from 'rxjs';
import { text } from '../../../node_modules/@angular/core/src/render3/instructions';

@Injectable()
export class CalculatorService {
    public stringSubject = new Subject<any>();
    myMethod$: Observable<any>;
    private myMethodSubject = new Subject<any>();
    private messageSource = new BehaviorSubject('default message');
    private messageSource2 = new BehaviorSubject('default message');
    currentMessage = this.messageSource.asObservable();
    currentMessage2 = this.messageSource2.asObservable();
  constructor(private http: HttpClient) {
    this.myMethod$ = this.myMethodSubject.asObservable();
   }

   changeMessage(message: string, inputers: string) {
    this.messageSource.next(message);
    this.messageSource2.next(inputers);
  }

   getSignature(id: number) {
    return this.http.get<any>(environment.api_url + '/api/signature/' + id + '/');
}

getsFileHeader(type: string, string: string ) {
    let headers = new HttpHeaders();
    headers = headers.set('Accept', 'text/' + type);
    return this.http.get(environment.api_url + '/api/calculator/?f=' + string,
     { headers: headers, responseType: 'blob' });
}

   public downloadUrl(data: any, filename: string, type: any): void {
    const file = new Blob([data], {type: 'text/' + 'text/xlxs' });
    const url = URL.createObjectURL(file);
    const hiddenAnchor = document.createElement('a');
    hiddenAnchor.href = url;
    hiddenAnchor.target = '_blank';
    hiddenAnchor.style.display = 'none';
    if (filename) { (<any>hiddenAnchor).download = filename; }
    document.body.appendChild(hiddenAnchor);
    hiddenAnchor.click();
}

  upload(data: FormData, data2: any) {
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
          xhr.open('POST', environment.api_url + '/api/type/' + data2 + '/', true);
          xhr.setRequestHeader('Authorization', bearer);
          xhr.upload.onprogress = (event) => {
            console.log( Math.round(event.loaded / event.total * 100) + '%' );
            if (event.lengthComputable) {
                console.log('sss', event.total);
                console.log('aaa', event.loaded);
                console.log( Math.round(event.loaded / event.total * 100) + '%' );
                this.dataupload(Math.round(event.loaded / event.total * 100));
                this.stringSubject.next( Math.round(event.loaded / event.total * 100));
              }
        };


          xhr.send(data);
      });
    }
dataupload(numberupload: any) {
    console.log('numberrrresss', numberupload);
    return  numberupload;
}
myMethod(data) {
    console.log('dsadasd22131tttttttttttttttttttttttttuiiiiiii', data); // I have data! Let's return it so subscribers can use it!
    // we can do stuff with data if we want
    this.myMethodSubject.next(data);
}

    passValue(data2) {
        this.stringSubject.next(data2);
      }

}
