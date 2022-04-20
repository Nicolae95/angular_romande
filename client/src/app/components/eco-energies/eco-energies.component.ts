import { Component, OnInit } from '@angular/core';
import { RiscService } from '../../_services';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-eco-energies',
  templateUrl: './eco-energies.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/theme.css'
  ]
})
export class EcoEnergiesComponent implements OnInit {
  chart: any;
  loading: boolean;
  valute = 'CHF';
  market = false;
  year: number;
  yearList: number[] = [];
  count: number;
  dates: any[] = [];

  transform(arr: Array<any>): any {
    return arr.sort((a, b) => {
      if (a > b) {return  1; }
      if (a < b) {return -1; }
      return 0;
    });
  }

  constructor(private riscService: RiscService,
              private toastr: ToastrService) {
  }


  showSuccess(mesaj: string) { this.toastr.success(mesaj); }
  showError(mesaj: string) { this.toastr.error(mesaj); }

  ngOnInit() {
    this.year = new Date().getFullYear() + 1;
    for (let y = this.year; y < this.year + 4; y++) {
      this.yearList.push(y);
    }
    this.getRisq(this.year, this.market);
  }

  getRisq(year: number, market: boolean) {
    this.year = year;
    this.market = market;
    this.loading = true;
    this.chart = null;

    this.riscService.getPfcRisqs(year, market).subscribe(
      (data) => {
        this.chart = data;
        this.loading = false;
        this.transform(data['pfcs']);
        // console.log('chart', this.chart);
        // this.count = this.chart['records']['Mix hydro-solaire suisse'].length - 20;
        // console.log('count', this.count);
        // this.chart['records']['Mix hydro-solaire suisse'].forEach((element, index) => {
        //   if (index >= this.count) { this.dates.push(element[0]); }
        // });
        // console.log('dates', this.dates);
      },
      (e) => { this.loading = false; },
      () => { this.loading = false;  }
    );
  }

}
