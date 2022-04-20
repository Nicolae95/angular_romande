import { User } from './../../_models/user';
import { Offer } from './../../_models/offer';
import { Component, OnInit,  Input } from '@angular/core';
import { OfferService } from '../../_services/offer.service';
import 'rxjs/add/operator/switchMap';
import { ReloadService } from '../../_services/reload.sevice';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-inf-offer',
  templateUrl: './inf-offer.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/theme.css'
  ]
})
export class InfOfferComponent implements OnInit {
  @Input() idOffer: any;
  currentUser: User;
  year: number;
  yearList: number[] = [];
  offer: Offer;
  nameO: any;
  budgets: any;
  resume = true;
  loading = false;
  chartByYears: any;
  surgoElemnts: any[] = [];
  efortElemnts: any[] = [];
  volumesByOffert: any;
  nomTypeOffer: any;
  nomServ: any;
  aniiLissge = [];
  numaAniiLisage = [];
  numaAniiDecote = [];
  id: number;
  lc: any;
  ac: any;

  constructor(
              private reloadService: ReloadService,
              private activatedRoute: ActivatedRoute,
              private router: Router,
              private offerService: OfferService) {
              this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
              this.activatedRoute.params.subscribe( params =>  {this.id = params.id; });
              this.activatedRoute.params.subscribe( params =>  {this.lc = params.lc; });
              this.activatedRoute.params.subscribe( params =>  {this.ac = params.c; });
  }

  ngOnInit() {
    if (this.id) { this.getOffer(this.id); } else { this.router.navigate(['account']); }
    this.reloadService.isReloadEditOffer.subscribe(
      (data) => {
        if (data === true) {
          this.getOffer(this.idOffer);
          this.reloadService.changeEditOffer(false);
        }
      },
      (er) => { this.router.navigate(['account']); }
    );
    this.year = new Date().getFullYear();
    for ( let y = this.year; y < this.year + 6; y++) { this.yearList.push(y); }
    if (this.offer !== undefined) {this.router.navigate(['../offers']); }
  }

  retour () {
    if (this.lc = 'account') { this.router.navigate(['account/offers/', this.ac]); }
    if (this.lc = 'cockpit') { this.router.navigate(['cockpit']); }
    if (this.lc = 'offers') {  this.router.navigate(['offers']); }

  }

  getOffer(idO: number) {
    this.offerService.getById(idO).subscribe(
      (data) => {
        this.offer = data;
        console.log('data', data);
        this.loading = false;
        this.getBudget(this.offer.id);
        this.getVolumes(this.offer.id);
        if (this.offer.energy_type) {
          if (this.offer.energy_type === 'energy1') {
            this.nomTypeOffer = 'Certificats hydrauliques suisses naturemade star';
            this.nomServ = 'Hydro Naturemade Star suisse'; // nume pe server
          }
          if (this.offer.energy_type === 'energy2') {
            this.nomTypeOffer = 'Certificats hydrauliques suisses';
            this.nomServ = 'Hydro suisse'; // nume pe server
          }
          if (this.offer.energy_type === 'energy3') {
            this.nomTypeOffer = 'Certificats nucléaires suisses';
            this.nomServ = 'Nucléaire suisse'; // nume pe server
          }
          if (this.offer.energy_type === 'energy4') {
            this.nomTypeOffer = 'Certificats mix hydrauliques-solaires suisses';
            this.nomServ = 'Mix hydro-solaire suisse'; // nume pe server
          }
          if (this.offer.energy_type === 'energy5') {
            this.nomTypeOffer = 'Certificats hydrauliques romands naturemade star';
            this.nomServ = 'Hydro Naturemade Star romand'; // nume pe server
          }
          if (this.offer.energy_type === 'energy6') {
            this.nomTypeOffer = 'Certificats hydrauliques européens';
            this.nomServ = 'Hydro européens'; // nume pe server
          }
          if (this.offer.energy_type === 'energy7') {
            this.nomTypeOffer = ' Hydro suisse Naturemade Basic';
            this.nomServ = 'Hydro suisse Naturemade Basic'; // nume pe server
          }
          if (this.offer.energy_type === 'energy8') {
            this.nomTypeOffer = 'Solaire suisse Naturemade Star';
            this.nomServ = 'Solaire suisse Naturemade Star'; // nume pe server
          }
          if (this.offer.energy_type === 'energy9') {
            this.nomTypeOffer = this.offer.custom_eco;
            this.nomServ = 'Custom'; // nume pe server
          }
        }
      },
      (err) => { this.loading = false; }
    );
  }

  getBudget(id: number) {
    this.loading = true;
    this.aniiLissge.length = 0;
    this.budgets = null;
    this.offerService.getBudget(id).subscribe(
      (data) => {
         this.budgets = data;
         this.loading = false;
         console.log('bugets', this.budgets);
        //  this.totatEco();
         this.numaAniiDecote.length = 0;
          this.budgets.years.forEach(anee => {
            this.numaAniiDecote.push(anee);
         });

        // toata logica cu anii lisage sau decote
        // scoatem numai anii care is lissage
        if (this.budgets.lissages.length > 0) {
          this.budgets.lissages.forEach(doi => {
            for (const key in doi) {
              if (doi.hasOwnProperty(key)) {
                this.numaAniiLisage.push(Number(key));
              }
            }
          });
          //  stergem anii lisage din lista cu ani si cei care ramin eventual sunt decote
          this.budgets.years.forEach((decote1, index) => {
            this.numaAniiLisage.forEach(liss1 => {
              if ( decote1 === liss1 ) { delete this.numaAniiDecote[index]; }
            });
          });
          // console.log('numaAniiDecote', this.numaAniiDecote);
          this.numaAniiDecote.forEach(ddd => {
            this.aniiLissge.push({year: ddd, type: 'decote' });
          });
          // punem anul si tipul  lisage (doar care is lisage)
          this.budgets.years.forEach(unu => {
            this.numaAniiLisage.forEach(doi => {
              if (doi ===  unu) { this.aniiLissge.push({year: unu, type: 'lissage' }); }
            });

          });
        } else {
          // daca nus ani lisage ii punem toti ca ani  lisage ca sa ii afiseze cu background white
          this.budgets.years.forEach(trei => {
            this.aniiLissge.push({year: trei, type: 'lissage' });
          });
        }


        // console.log('aniiLissge', this.aniiLissge);


        },
        (err) => { this.loading = false;  }
    );

    this.offerService.getBudgetHistory(id).subscribe(
      (data) => { this.chartByYears = data; this.loading = false; },
      (err) => { this.loading = false; }
    );
  }

  setyear(year: number) { this.year = year; }
  getVolumes(id: number) {
    this.offerService.getVolumes(id).subscribe(
      (data) => {this.volumesByOffert = data; }
    );
  }


  // totatEco() {
  //   this.budgets.parameters_records.forEach(element => {
  //     if (element.parameter__name === 'Marge sur GO') { this.surgoElemnts.push(element);  }});

  //   this.budgets.riscs_records.forEach(element => {
  //     if (element.risc__code === this.offer.energy_type) {  this.efortElemnts.push(element);  }});


  //     const a = [];
  //     this.budgets.riscs_records.forEach(element => {
  //       if (element.risc__code !== this.offer.energy_type) { a.push(element.risc__name); }
  //     });

  //     const b = [];
  //     for (let index = 0; index < a.length - 1; index++) {
  //       if (index === 0) { b.push(a[index]); }
  //       if (a[index] !== a[index + 1])  {  b.push(a[index + 1]); }
  //     }

  //     this.budgets.riscs_records.forEach(element => {
  //         if (element.risc__name === b[0]) { this.risqPwb.push(element); }});

  //     this.budgets.riscs_records.forEach(element => {
  //       if (element.risc__name === b[1]) { this.risqprix.push(element); }});

  //     this.budgets.riscs_records.forEach(element => {
  //       if (element.risc__name === b[2]) { this.risqvolume.push(element); }});


  //   // calculate sume of sur go and eco energy
  //     this.surgoElemnts.forEach(surGo => {
  //       this.efortElemnts.forEach(eco => {
  //       if (surGo.year === eco.year) {  this.totals.push( {value: surGo.value + eco.value, year: surGo.year});  }
  //       });
  //     });

  //   // calculate sume to risque
  //   this.risqPwb.forEach(unu => {
  //     this.risqprix.forEach(doi => {
  //       this.risqvolume.forEach(trei => {
  //         if (unu.year === doi.year && doi.year === trei.year) {
  //           this.totalsRisc.push( {value: unu.value + doi.value + trei.value, year: unu.year});
  //         }
  //       });
  //     });
  //   });
  // }
}
