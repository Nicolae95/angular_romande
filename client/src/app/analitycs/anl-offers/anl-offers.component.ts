import { Component, OnInit} from '@angular/core';
import { FormGroup, FormControl} from '@angular/forms';
import 'rxjs/add/operator/switchMap';
import { SearchService, UserService } from '../../_services';
import { Pagination } from '../../_models/pagination';
import { User } from '../../_models';

@Component({
  selector: 'app-anl-offers',
  templateUrl: './anl-offers.component.html',
  styleUrls: [
  // '../../../assets/css/styles.css',
  // '../../../assets/css/styles/nexus.css',
  // '../../../assets/css/styles/layout.css',
  // '../../../assets/css/styles/theme.css',
  '../../../assets/css/theme_analytics.css',
  '../../../assets/css/layout_analytics.css'
  ]
})
export class AnlOffersComponent implements OnInit {
  offerPagination: Pagination<any>;
  currentUser: User;
  show = [false];
  loading = false;
  voirYear = [false];
  pag = 1;
  nr: number;
  ofGroup: FormGroup;
  search: FormControl;
  keyword = '';

  allOrUne = false;
  userActiv = null;


  constructor(private searchService: SearchService,
              private userService: UserService,
              ) {  this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
                   this.nr = this.currentUser.nr; }

  ngOnInit() {

    this.search = new FormControl('');
    this.ofGroup = new FormGroup({search: this.search});
    this.onChangesSearsh();

  }

  onChangesSearsh(): void {
    this.ofGroup.get('search').valueChanges
    .debounceTime(200)
    .distinctUntilChanged()
    .subscribe(val => {
      this.pag = 1;
      this.obsevableSearsh(val);
    });
  }


  obsevableSearsh(keyword: string) {
    this.keyword = keyword;
      this.searchService.searchNamePag(keyword, '', this.pag , '', this.nr)
      .subscribe (
        (data) => {
          this.show = [false];
          this.offerPagination = data;
          // this.offerPagination.result.forEach(element => {
          //   const y = String(element.years);
          //   element.yearsSplits = y.split(',');
          //  });
          // console.log('offerPagination', this.offerPagination);

        },
        (er) => {  this.keyword = null; },
    );
  }
  pags(pag) { this.pag = pag; this.obsevableSearsh(this.keyword); }

  setNumberperPag(nr: number) {
    this.nr = Number(nr);
    this.userService.chnageNrPerPag(this.currentUser, nr).subscribe((data) => { this.pags(1); });
  }



  voir(of: any) {
    this.allOrUne = true;
    const userActiv1 = {'id': of.company, 'last_offer': of.id};
    this.userActiv = userActiv1;
  }
}

