import { User } from './../../_models/user';
import { Offer } from './../../_models/offer';
import { CcService } from './../../_services/cc.service';
import { Component, OnInit , Input } from '@angular/core';
import { OfferService } from '../../_services/offer.service';
import 'rxjs/add/operator/switchMap';
import { PfcService, RiscService, SearchService, CustomObservable } from '../../_services';
import { Router } from '@angular/router';

@Component({
  selector: 'app-inf-offer-mail',
  templateUrl: './inf-offer-mail.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/theme.css'
  ]
})
export class InfOfferMailComponent implements OnInit {
  @Input() idOffer: any;
  @Input() token: string;
  currentUser: User;
  year: number;
  yearList: number[] = [];
  offer: Offer;
  nameO: any;
  budgets: any;
  resume = true;
  loading = false;
  msg: string;
  showBottomPane = true;
  chartByYears: any;

  constructor(private ccService: CcService,
              private router: Router,
              private offerService: OfferService) {
              this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
  }

  ngOnInit() {
    this.year = new Date().getFullYear();
    for ( let y = this.year; y < this.year + 6; y++) { this.yearList.push(y); }

    this.offerService.getById(this.idOffer).subscribe(
      (data) => {
        this.offer = data;
        this.loading = false;
        this.getBudget(this.offer.id);
      },
      (err) => { this.loading = false; }
    );

    // console.log('offer:', this.offer);
    if (this.offer !== undefined) {
      this.router.navigate(['../offers']);
    }
  }

  getBudget(id: number) {
    this.loading = true;
    this.offerService.getBudget(id).subscribe(
      (data) => {
        console.log('budgets:', data);
        this.budgets = data;
        this.loading = false;
      },
      (err) => {
        this.loading = false;
      }
    );
    this.chartByYears = null;
    this.offerService.getBudgetHistory(this.idOffer).subscribe(
        (data) => { this.chartByYears = data; this.loading = false; },
        (err) => {this.loading = false;  this.chartByYears = null; }
      );
  }

  setyear(year: number) { this.year = year; }

  acceptOffer(accepted: boolean) {
    this.showBottomPane = false;
    if (accepted) {
      this.msg = 'Votre demande a bien été enregistrée. Vous serez contacté par email dans les meilleurs délais.';
    } else {
      this.msg = 'Merci pour votre réponse.';
    }

    const acc = {accepted: accepted};
    this.ccService.acceptedOffer(this.token, acc).subscribe(
      (data) => {},
      (err) => {}
    );
  }

}
