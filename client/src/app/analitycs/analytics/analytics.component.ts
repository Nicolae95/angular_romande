import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { UserService, AuthenticationService, CustomObservable } from '../../_services';
import { ReloadService } from '../../_services/reload.sevice';
import { AnalyticsService } from '../../_services/analytics';
import { User } from '../../_models';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-analytics',
  templateUrl: './analytics.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
    // '../../../assets/css/styles/animate.css'
    '../../../assets/css/theme_analytics.css',
    '../../../assets/css/layout_analytics.css'
  ]
})
export class AnalyticsComponent implements OnInit {
  currentUser: User;
  users: User[] = [];
  isLoggedIn$: Observable<boolean>;
  accountUrl = false;
  showNotifications: boolean;
  topUser: any;
  alarm_A = false;
  notif_A = false;
  expression = false;

  constructor(private userService: UserService,
              private router: Router,
              private reloadService: ReloadService,
              private authService: AuthenticationService,
              private analyticsService: AnalyticsService,
              private customObservable: CustomObservable
            ) {
    this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
   }

  ngOnInit() {
    this.loadAllUsers();
    this.isLoggedIn$ = this.authService.isLoggedIn;
    if ( this.router.url.slice(0, 8) === '/account') {
      this.accountUrl = true;
    } else { this.accountUrl = false; }
    this.getNotifications();
    setInterval(() => this.getNotifications(), 35000);
  }

  account() { this.reloadService.changeCC(true); }

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

}
