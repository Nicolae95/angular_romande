import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable()
export class FileService {
    token: any;

  constructor(private http: HttpClient) {
    this.token = JSON.parse(localStorage.getItem('token'));
   }


    getSignature(id: number) {
        return this.http.get<any>(environment.api_url + '/api/signature/' + id + '/');
    }

    getsFileHeader(url: any, headers: any) {
        return this.http.get(environment.api_url + '/api/' + url, { headers: headers, responseType: 'blob' });
    }



    downloadUrl(data: any, filename: string, type: any): void {
        const file = new Blob([data], {type: 'application/' + type });
        const url = URL.createObjectURL(file);
        const hiddenAnchor = document.createElement('a');
        hiddenAnchor.setAttribute('id', filename);
        hiddenAnchor.href = url;
        hiddenAnchor.target = '_blank';
        hiddenAnchor.style.display = 'none';
        if (filename) { (<any>hiddenAnchor).download = filename; }
        document.body.appendChild(hiddenAnchor);
        hiddenAnchor.click();

        setTimeout(function() {
          document.body.removeChild(hiddenAnchor);
          window.URL.revokeObjectURL(url);
          }, 200);
    }

}


