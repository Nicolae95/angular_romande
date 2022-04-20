import { Component, OnInit } from '@angular/core';
import { UserService, AuthenticationService } from './_services';
import { Router, NavigationEnd, } from '@angular/router';
import { Observable } from 'rxjs/Observable';
import { Title } from '@angular/platform-browser';
import { environment } from '../environments/environment.prod';

@Component({
    moduleId: module.id.toString(),
    // tslint:disable-next-line:component-selector
    selector: 'app',
    templateUrl: 'app.component.html',
    styleUrls: [
        // '../assets/css/styles.css'
    ]
})

export class AppComponent implements OnInit {
    loged: boolean;
    currentUser: any;
    isLoggedIn$: Observable<boolean>;
    dataSource: Object;
    title: string;
    enviroment: any;
    environment = environment.api_url;
    token: any;

    constructor(private userService: UserService,
                private authService: AuthenticationService,
                private router: Router,
                private titleService: Title,
                ) {
            this.token = JSON.parse(localStorage.getItem('token'));
             router.events.subscribe(event => {
            if ( event instanceof NavigationEnd ) {
                const title = this.getTitle(router.routerState, router.routerState.root).join(' '); titleService.setTitle(title);
            }});
    }

    ngOnInit() {
        this.getUser();
        this.isLoggedIn$ = this.authService.isLoggedIn;
    }

    private getUser() {
        this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
        this.userService.getUser().subscribe(
            user => {this.loged = true; },
            err => {this.loged = false; }
        );
    }

    getTitle(state, parent) {
        const data = [];
        if ( environment.api_url !== 'https://energysalesengine.com') {
            if (parent && parent.snapshot.data && parent.snapshot.data.title) {
            data.push(parent.snapshot.data.title);
            }
            if (state && parent) {
            data.push(... this.getTitle(state, state.firstChild(parent)));
            }
        } else {  data.push('Tata'); }
        return data;
    }

 }
