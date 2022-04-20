import { User } from './../../_models/user';
import { Component, OnInit } from '@angular/core';
import { UserService, AuthenticationService, CustomObservable, CcService } from '../../_services/index';
import { Observable } from 'rxjs/Observable';
import { Router, NavigationStart } from '@angular/router';
import { ReloadService } from '../../_services/reload.sevice';
import { AnalyticsService } from '../../_services/analytics';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: [ './header.component.css', '../../../assets/css/animate.css' ]
})

export class HeaderComponent implements OnInit {
  currentUser: User;
  users: User[] = [];
  isLoggedIn$: Observable<boolean>;
  accountUrl = false;
  dataUrl = false;
  courbesUrl = false;

  showNotifications: boolean;
  topUser: any;
  alarm_A = false;
  notif_A = false;


  data = false;
  courbes = false;
  notifications = false;
  accountsRout = false;
  accordion_hide = true;
  hamburger_mobile = false;
  token: any;
  unauthorized: boolean;
  accounts = false;
  curentClient: any;


  constructor(private userService: UserService,
              private router: Router,
              private ccService: CcService,
              private reloadService: ReloadService,
              private authService: AuthenticationService,
              private analyticsService: AnalyticsService,
              private customObservable: CustomObservable
            ) {
    this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
    this.token = JSON.parse(localStorage.getItem('token'));

    router.events.subscribe(event => {
      try {
        if (event instanceof NavigationStart) {this.whatUrlIs(event.url); }
      } catch (error) { }
    });
   }

  ngOnInit() {
    this.userService.getUser().subscribe(
      (data) => { this.unauthorized =  false;  },
      (er) => { this.unauthorized =  true;  }
      );
    if (this.currentUser) {
    this.loadAllUsers();
    this.isLoggedIn$ = this.authService.isLoggedIn;
    this.whatUrlIs(this.router.url);
    this.getNotifications();
    setInterval(() => this.getNotifications(), 35000);
    this.getcurentClient();
  }
  }

  whatUrlIs(url: any) {
    this.accountUrl = false;
    this.dataUrl = false;
    this.courbesUrl = false;
    if ( url === '/clients' || url === '/admins') { this.accountUrl = true; }
    if ( url === '/pfc' || url === '/risque' || url === '/ecoenergies' || url === '/datahub') { this.dataUrl = true; }
    if ( url === '/pondere' || url === '/conversiontool') { this.courbesUrl = true; }

  }

  account() {
    this.reloadService.changeCC(true);
  }

  private loadAllUsers() {
    this.userService.getAll().subscribe(users => { this.users = users; });
  }

  getNotifications() {
    this.alarm_A = false;
    this.notif_A = false;
    this.analyticsService.getClientLogTop(this.currentUser.id).subscribe(
      (data) => {
        this.topUser = data;
      if (this.topUser.nr !== 0) {this.alarm_A = true; }}
    );
  }

  voirAll() {
    this.showNotifications = false;
    this.customObservable.changeNotification(true);
  }

  getcurentClient() {
    this.curentClient = null;
    this.ccService.getClient(this.currentUser.id).subscribe((data) => { this.curentClient = data; });
  }

}
