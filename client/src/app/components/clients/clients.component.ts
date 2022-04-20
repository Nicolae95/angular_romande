import { Component, OnInit } from '@angular/core';
import { Pagination } from '../../_models/pagination';
import { Company, User } from '../../_models';
import { CompanyService, CcService, SearchService, CustomObservable, UserService } from '../../_services';
import { FormGroup, FormControl } from '@angular/forms';
import { Router } from '@angular/router';
import { ReloadService } from '../../_services/reload.sevice';

@Component({
  selector: 'app-clients',
  templateUrl: 'clients.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
  ]

})
export class ClientsComponent implements OnInit {
  currentUser: User;
  companyPagination: Pagination<any>;
  pag = 1;
  nom = '';
  headForm: FormGroup;
  search: FormControl;
  keyword = '';
  showDropDown = false;
  companies: Company[] = [];
  company: Company;
  nouveau_client = false;
  voirAllO = [false];
  voirCok = [false];
  nr: number;

  constructor(private companyService: CompanyService,
              private ccService: CcService,
              private searchService: SearchService,
              private router: Router,
              private userService: UserService,
              private customObservable: CustomObservable,
              private reloadService: ReloadService,
               ) { this.currentUser = JSON.parse(localStorage.getItem('currentUser')); this.nr = this.currentUser.nr; }

  ngOnInit() {
    this.search = new FormControl();
    this.headForm = new FormGroup({search: this.search});
    this.onChanges();
    this.reloadService.isReloadClient.subscribe(
      (data) => {
        if (data === true) {
          this.observableSource('');
          this.nouveau_client = false;
          this.reloadService.changeReloadClient(false);
        }
      }
    );

  }

  getAlls(pag: number, nom: string) {
    this.pag = pag;
    this.companyService.getAll(pag, nom, this.nr).subscribe(
      (data) => {
      this.companyPagination = data;
      // default
      // this.saveCompany(this.companyPagination.result[0]);
    }
    );
  }

    onChanges(): void {
      this.headForm.get('search').valueChanges
      .debounceTime(200)
      .distinctUntilChanged()
      .subscribe(val => {
        this.observableSource(val);
      });
      this.ccService.change(null);
    }

    observableSource(keyword: string) {
      if (keyword === '') {
        this.saveCompany(null);
        this.companies = null;
        this.getAlls(this.pag, keyword);
      }
      if (keyword !== '') {
      this.keyword = keyword;
      this.getAlls(this.pag, keyword);
        this.searchService.searchCompany(keyword)
        .subscribe (
          (data) => {
            this.companies = data;
          },
          (er) => { this.keyword = null; },
      );
      }
    }

    pags(pag: number) {
      this.pag = pag;
      this.observableSource(this.keyword);
    }

    setNumberperPag(nr: number) {
      this.nr = Number(nr);
      this.userService.chnageNrPerPag(this.currentUser, nr).subscribe((data) => { this.pags(1); });
    }

    closeDropDown() {this.showDropDown = false; }
    openDropDown() {this.showDropDown = true; }

    saveCompany(company: Company) {
      if (company) {
        this.company =  company;
        this.customObservable.changeCompany(this.company);
        this.router.navigate(['account/offers/', company.id]);
      }
    }

    // returnSplitedYears() {
    //   console.log('companyPagination', this.companyPagination );
    //   // this.companyPagination.result.forEach(element => {
    //   //  const coc = String(element.cockpits);
    //   //  const off = String(element.offers);
    //   //  element.cokpitsSp = coc.split(',');
    //   //  element.offersSp = off.split(',');
    //   // });
    // }
}

