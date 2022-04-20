import { Component, OnInit } from '@angular/core';
import { DashboardService } from '../../_services/dashboart.service';
import { CustomObservable } from '../../_services';
import { OfferService } from '../../_services/offer.service';
const PADDING = '000000';

@Component({
  selector: 'app-site-dashboard',
  templateUrl: './site-dashboard.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css'
]
})
export class SiteDashboardComponent implements OnInit {
  dashbord: any;
  year: number;
  months = [];
  chart: any;
  chartSeason: any;
  weekly: {};
  site: any;
  budgets: any;
  private DECIMAL_SEPARATOR: string;
  private THOUSANDS_SEPARATOR: string;
  volume_1 = '0';
  volume_2 = '0';
  volume_3 = '0';
  volume_4 = '0';
  totals_5  = '0';
  maxVolumeCc: any;
  local_hedges_diagram = false;


  constructor(private dashboardService: DashboardService,
              private offerService: OfferService,
              private customObservable: CustomObservable,
              ) {   this.DECIMAL_SEPARATOR = '.';
                    this.THOUSANDS_SEPARATOR = '\''; }


    transform(value: number | string, fractionSize: number = 2): string {
      let [ integer, fraction = '' ] = (value || '').toString()
        .split(this.DECIMAL_SEPARATOR);

      fraction = fractionSize > 0
        ? this.DECIMAL_SEPARATOR + (fraction + PADDING).substring(0, fractionSize)
        : '';
      integer = integer.replace(/\B(?=(\d{3})+(?!\d))/g, this.THOUSANDS_SEPARATOR);
      return integer + fraction;
    }

  ngOnInit() {
    // console.log('budgets', this.budgets);
    this.months.push({'itemName' : 'Jan', 'id' : '1'}, {'itemName' : 'Fév', 'id' : '2'}, {'itemName' : 'Mar', 'id' : '3'},
                     {'itemName' : 'Avr', 'id' : '4'}, {'itemName' : 'Mai', 'id' : '5'}, {'itemName' : 'Jun', 'id' : '6'},
                     {'itemName' : 'Jul', 'id' : '7'}, {'itemName' : 'Aoû', 'id' : '8'}, {'itemName' : 'Sep', 'id' : '9'},
                     {'itemName' : 'Oct', 'id' : '10'}, {'itemName' : 'Nov', 'id' : '11'}, {'itemName' : 'Déc', 'id' : '12'});
    this.customObservable.isSite.subscribe((data) => {
      this.site = data;
      if (this.site) {
       this.getDashbord(this.site.id, this.site.year);
      }
    }, (err) => {});
  }

  getDashbord(id: number, year: any) {
    this.year = year;
    this.dashbord = null;
    this.chart = null;
    this.chartSeason = null;
    this.weekly = null;
    this.dashboardService.getDashboard(id, year).subscribe(
      (data) => {
        this.dashbord = data;
        console.log('dashbord', this.dashbord);
        this.chart = data.months_diagram;
        this.chartSeason = data.season_value;
        this.getConst();
        this.customObservable.changeVolume(data.months_total);
        this.customObservable.changeYear(this.year);
        this.volumetab();
        let tot = this.dashbord.months_total.Total.value__sum.replace(/[^0-9.]/g, '');
            tot = Number(tot); this.totals_5 =  this.transform(tot / 1000, 0);
      },
      (err) => { }
    );
  }

  setyear(y: any) {
    this.year = y;
    this.getDashbord(this.site.id, this.year);
  }

  volumetab() {
    this.dashbord.season_value.forEach(e => {
    if ( e.season === 'Winter' && e.schedule__title === 'Peak')    { this.volume_1 = this.transform(e.value / 1000, 0); }
    if ( e.season === 'Winter' && e.schedule__title === 'OffPeak') { this.volume_2 = this.transform(e.value / 1000, 0); }
    if ( e.season === 'Summer' && e.schedule__title === 'Peak')    { this.volume_3 = this.transform(e.value / 1000, 0); }
    if ( e.season === 'Summer' && e.schedule__title === 'OffPeak') { this.volume_4 = this.transform(e.value / 1000, 0); }
    });
  }

  getConst() {
    this.offerService.getConstants().subscribe((data) => {
      data.forEach(e => { if (e.id === 5) { this.maxVolumeCc = e.value * 1000000; } });
      console.log('hedges', this.maxVolumeCc, '<', Number(this.dashbord.months_total.Total.value__sum.replace(/[^0-9.]/g,  '')));
      if (this.maxVolumeCc <  Number(this.dashbord.months_total.Total.value__sum.replace(/[^0-9.]/g,  ''))) {
        this.weekly = { weekly_value:  this.dashbord.weekly_value, hedges_diagram: this.dashbord.hedges_diagram };
         this.local_hedges_diagram = true;
      } else { this.weekly = { weekly_value:  this.dashbord.weekly_value, hedges_diagram: [] }; this.local_hedges_diagram = false; }

    });
  }
}
