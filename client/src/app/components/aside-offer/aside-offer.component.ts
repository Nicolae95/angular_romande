
import { User } from './../../_models/user';
import { Company } from './../../_models/company';
import { Offer } from './../../_models/offer';
import { CompanyService } from './../../_services/company.service';
import { Component, OnInit , Input } from '@angular/core';
import { OfferService } from '../../_services/offer.service';
import 'rxjs/add/operator/switchMap';
import { RiscService, CustomObservable } from '../../_services';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';


@Component({
  selector: 'app-aside-offer',
  templateUrl: './aside-offer.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/theme.css'
  ]
})
export class AsideOfferComponent implements OnInit {
  @Input() aside: any;
  currentUser: User;
  offer: Offer;
  nameO: any;
  budgets: any;
  resume = true;
  loading = false;
  company: Company;
  edit = false;
  environment = environment.api_url;


  constructor(private router: Router,
              private companyService: CompanyService,
              private customObservable: CustomObservable,
              private offerService: OfferService,
              private riscService: RiscService) {
              this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
  }

  ngOnInit() {
    this.offerService.getById(this.aside).subscribe(
      (data) => {
        this.offer = data;
        this.loading = false;
        this.getBudget(this.offer.id);
        this.getcompany(this.offer.company);
      },
      (err) => { this.loading = false; }
    );

    if (this.offer !== undefined) {
      this.router.navigate(['../offers']);
    }

  }

  getcompany(id: number) {
    this.companyService.getCompanyById(id).subscribe(
      (data) => { this.company = data; }
    );
  }


  getBudget(id: number) {
    this.loading = true;
    this.offerService.getBudget(id).subscribe(
      (data) => {
        this.budgets = data;
        this.loading = false;
        // console.log('budgets:', this.budgets);
      },
      (err) => {
        this.loading = false;
      }
    );
  }

  editOffer() { this.customObservable.changeEditOffer(this.offer); }
}

