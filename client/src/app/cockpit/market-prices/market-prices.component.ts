import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Chart } from 'angular-highcharts';
import * as Highcharts from 'highcharts';
import { SharableService, CockpitBService, DataHubService } from '../../_services';
import { Chartseries } from '../../_models';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-market-prices',
  templateUrl: './market-prices.component.html',
  styleUrls: ['./market-prices.component.css']
})

export class MarketPricesComponent implements OnInit {
    charts: any[];
    ids: string[] = [];
    wtfthis: string;
    objKeys: {};
    lines: any;
    chart: Chart;
    linedata: Chartseries = new Chartseries;
    curba: Chartseries[] = new Array<Chartseries>();
    href: any;
    active: any;
    sdelete: boolean;
    ajax: any;
    acolor: any;
    action: any;
    colors: string[] = ['#ffffff', '#37475a'];
    co: number;
    colorbg = '#ffffff';
    colorf = '#37475a';
    mpt = 'Market Prices & Trends';
    auxname: string;
    id: number;
    chartByMarkets: any;
    chartData: any;

    // chartByCock: any;

    constructor(private activatedRoute: ActivatedRoute,
                private dataHubService: DataHubService,
                private http: HttpClient,
                private cockpitBService: CockpitBService,
                private sharableService: SharableService
                ) {
      this.activatedRoute.params.subscribe( params =>  {this.id = Number(params.id); });
      }

  ngOnInit() {
    this.active = false;
    if (this.id) {
      this.chartsByCockpit(this.id);
      this.cockpitMarketById(this.id);
    }

  }

  getInEMP_tables(ids: any, index: number) {
    if (ids.length !== 0) {
      this.cockpitBService.getForTables(ids).subscribe(data => {
        // console.log('data', data['data']);
        // this.charts = data['data'];
        this.chartByMarkets[index].dataTab = data['data'];
        this.co = 2;

        this.sharableService.active.subscribe(acolor => this.acolor = acolor);
        this.sharableService.adel.subscribe(sdelete => this.sdelete = sdelete);

        this.sharableService.colorBg2.subscribe(bgc => this.colors[0] = bgc);
        this.sharableService.colorFont2.subscribe(fc => this.colors[1] = fc);

        this.sharableService.colorbg.subscribe(bgc => this.colorbg = bgc);
        this.sharableService.colorf.subscribe(fc => this.colorf = fc);
       });
    }





  }

  chartsByCockpit(id: number) {
    this.cockpitBService.getChartsByCockpit(id).subscribe(
      (data) => {
        const market_id = [];

        for (const key in data) {
          if (data.hasOwnProperty(key)) {
            const mark = data[key];
            mark.ids = [];
            mark.markets.forEach(e => {
              mark.ids.push(e.market_id);
            });
          }
        }
        for (const key in data) {
          if (data.hasOwnProperty(key)) {
            const mark = data[key];
            if (mark.ids.length !== 0) {
              this.getChartData(true, mark.ids, Number(key));
            }
          }
        }

        this.chartByMarkets = data;
        this.chartByMarkets.forEach((e, index) => {
          e.ids = e.ids.filter((el, i, a) => i === a.indexOf(el));

          this.getInEMP_tables(e.ids, index);
        });

        // console.log('ChartsByCockpit', this.chartByMarkets);
      },
      (er) => {},
    );
  }

  cockpitMarketById(id: number) {
    // this.cockpitBService.getCockpitMarketById(id).subscribe(
    //   (data) => { console.log('CockpitMarketBy', data); },
    //   (er) => {},
    // );
  }

  verify() {
    if (this.mpt.length < 4) { this.mpt = 'Market Prices & Trends'; }
  }

  offMe() {
    this.sharableService.changeActive(this.acolor);
    this.sharableService.changeCO(2);
    this.colorbg = this.colors[0];
    this.colorf = this.colors[1];
    this.sharableService.changeAuxColorBg(this.colorbg);
    this.sharableService.changeAuxColorF(this.colorf);
  }
  offMee() {
    this.sharableService.changeDel(this.sdelete);
  }

  getChartData(toStartChart: boolean, ids: Array<number>, index: number): void {
    if (toStartChart) {
        const tobj: any = {
          MarketID:  [],
          DateStart: '2018-10-16',
          DateEnd: '2018-11-16',

        };
        tobj.MarketID.push(ids);
          // tobj.MarketID =  this.selectedMarketsList.map((ob: any) => {
          //   return ob.market_id;
          // });

        tobj.MarketID =  ids;
        tobj.DateStart = '2018-11-09';
        tobj.DateEnd = '2018-11-16';

        // this.datePipe.transform(new Date(this.dateFrom.date.year, this.dateFrom.date.month - 1, this.dateFrom.date.day), 'yyyy-MM-dd');
        // this.datePipe.transform(new Date(this.dateTo.date.year, this.dateTo.date.month - 1, this.dateTo.date.day), 'yyyy-MM-dd');

        this.dataHubService.getChartData(tobj).subscribe(
          (chartData: any[]) => {
            this.chartByMarkets[index].result = chartData;
            // console.log('fin', this.chartByMarkets);
            this.chartData = chartData;

          },
          (er) => { }
        );
    }
  }

}





