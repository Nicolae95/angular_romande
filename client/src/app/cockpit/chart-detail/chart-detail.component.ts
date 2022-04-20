import { Component, OnInit, Input } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MarketPricesComponent } from '../market-prices/market-prices.component';

@Component({
  selector: 'app-chart-detail',
  templateUrl: './chart-detail.component.html',
  styleUrls: ['./chart-detail.component.css']
})


export class ChartDetailComponent implements OnInit {


@Input() takeMe: string;
@Input() title: string;

  dateFrom: any = new Date();
  dateTo: any = new Date();

  constructor(private marketPricesComponent: MarketPricesComponent) { }

  ngOnInit() {
    this.dateFrom.setDate(this.dateFrom.getDate() - 365);
    this.dateFrom = this.dateToDMY(this.dateFrom);
    this.dateTo = this.dateToDMY(this.dateTo);
  }

  drawChart(from, to) {
    this.dateFrom = from;
    this.dateTo = to;
    // console.log(this.dateFrom);
    // console.log(this.dateTo);
  }

dateToDMY(date) {
    const d = date.getDate();
    const m = date.getMonth() + 1;
    const y = date.getFullYear();
    return '' + (d <= 9 ? '0' + d : d) + '/' + (m <= 9 ? '0' + m : m) + '/' + y;
}

close() {
  this.takeMe = null;
  this.title = null;
  this.marketPricesComponent.ajax = null;
  this.marketPricesComponent.auxname = null;
}

}
