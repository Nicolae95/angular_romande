import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import 'rxjs/add/operator/map';
import { environment } from '../../environments/environment';
import { OfferService } from './offer.service';
import { User } from '../_models';

@Injectable()
export class AuthenticationService {
    alarm: boolean;
    data_user: User;
    private loggedIn = new BehaviorSubject<boolean>(false); // {1}


    constructor(private http: HttpClient, private offerService: OfferService) { }

    get isLoggedIn() {
        return this.loggedIn.asObservable(); // {2}
    }

    login(username: string, password: string) {
        return this.http.post<any>(environment.api_url + '/api/auth/login/', { username: username, password: password })
            .map(user => {
                // login successful if there's a jwt token in the response
                this.data_user = {
                    'id': user.user.pk,
                    'username': user.user.username,
                     'password': '',
                    'firstName': user.user.first_name,
                    'lastName':  user.user.last_name,
                    'email': user.user.email,
                    'role': user.user.role,
                    'fonction': user.user.fonction,
                    'alarm': true,
                    'nr': user.user.per_pag == null  ? 10 : user.user.per_pag ,
                };
                if (user && user.token) {
                    this.loggedIn.next(true);
                    // console.log(this.loggedIn.value);
                    // store user details and jwt token in local storage to keep user logged in between page refreshes
                    console.log('this.data_user', this.data_user);
                    localStorage.setItem('currentUser', JSON.stringify(this.data_user));
                    localStorage.setItem('token',       JSON.stringify(user.token));
                }
                this.getAalarm();
                return user;
            });
    }

    logout() {
        this.loggedIn.next(false);
        // remove user from local storage to log user out
        localStorage.removeItem('currentUser');
        localStorage.removeItem('token');
    }



    getAalarm() {
        this.offerService.get_alarm_Stop_Star().subscribe((date) => {
            this.alarm = date[0].stop;
            const story_reset = {
                    'id': this.data_user.id,
                    'username': this.data_user.username,
                    'password': this.data_user.password,
                    'firstName': this.data_user.firstName,
                    'lastName':  this.data_user.lastName,
                    'email': this.data_user.email,
                    'role': this.data_user.role,
                    'fonction': this.data_user.fonction,
                    'alarm': this.alarm,
                    'nr': this.data_user.nr == null  ? 10 : this.data_user.nr,
            };
            // console.log('story_reset', story_reset);
            localStorage.removeItem('currentUser');
            localStorage.setItem('currentUser', JSON.stringify(story_reset));
        });
    }

    resetPassword(username: any) {
        return this.http.put(environment.api_url + '/api/user/reset/pass/' + username + '/', {'username': username} );
    }


}
