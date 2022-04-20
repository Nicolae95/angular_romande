import { Component, OnInit } from '@angular/core';
import { AnalyticsService } from '../../_services/analytics';
import { LastActivity, User } from '../../_models';
import { Pagination } from '../../_models/pagination';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { UserService } from '../../_services';

@Component({
  selector: 'app-anl-activiti-client',
  templateUrl: './anl-activiti-client.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
    '../../../assets/css/theme_analytics.css',
    '../../../assets/css/layout_analytics.css'
  ]
})
export class AnlActivitiClientComponent implements OnInit {
  showUserActivity = false;
  activity: Pagination<LastActivity>;
  pag = 1;
  nr: number;
  activityGroup: FormGroup;
  search: FormControl;
  keyword = '';
  userActiv: any;
  currentUser: User;

  constructor( private analyticsService: AnalyticsService,
               private userService: UserService) {
                this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
                this.nr = this.currentUser.nr;
               }

  ngOnInit() {
    this.search = new FormControl('', Validators.required);
    this.activityGroup = new FormGroup({search: this.search});
    this.onChangesSearsh();
  }



  onChangesSearsh(): void {
    this.activityGroup.get('search').valueChanges
    .debounceTime(200)
    .distinctUntilChanged()
    .subscribe(val => {
      this.pag = 1;
      this.getLastActivity(val, this.pag, this.nr);
    });
  }

  getLastActivity(name: string, pag: number, nr: number) {
    this.analyticsService.getLastActivity(name, pag, nr).subscribe(
      (data) => { this.activity = data; },
      (er) => {}
    );
  }

  pags(pag: number) { this.pag = pag; this.getLastActivity(this.keyword, this.pag, this.nr); }

  setNumberperPag(nr: number) {
    this.nr = Number(nr);
    this.userService.chnageNrPerPag(this.currentUser, nr).subscribe((data) => { this.pags(1); });
  }

}
