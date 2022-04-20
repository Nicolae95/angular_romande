import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { User } from '../_models/index';

@Injectable()
export class UserService {
    constructor(private http: HttpClient) { }

    getAll() {
        return this.http.get<User[]>(environment.api_url + '/api/user/list/');
    }

    getUser() {
        return this.http.get<any>(environment.api_url + '/api/auth/user/');
    }

    getById(id: number) {
        return this.http.get(environment.api_url + '/api/user/id/' + id + '/');
    }

    create(user: User) {
        return this.http.post(environment.api_url + '/api/user/', user);
    }

    update(user: User) {
        return this.http.put(environment.api_url + '/api/user/id/' + user.id, user);
    }

    delete(id: number) {
        return this.http.delete(environment.api_url + '/api/user/' + id);
    }

    chnageNrPerPag(user: User, nr: number) {
    const toStory = {
        'id': user.id,
        'username': user.username,
        'firstName': user.firstName,
        'lastName':  user.lastName,
        'email': user.email,
        'role': user.role,
        'fonction': user.fonction,
        'alarm': user.alarm,
        'nr': nr
      };
    localStorage.removeItem('currentUser');
    localStorage.setItem('currentUser', JSON.stringify(toStory));
    return this.http.put(environment.api_url + '/api/user/page/' + user.id + '/', {'per_pag': nr});
    }
}
