import { Component, OnInit } from '@angular/core';
import { INgxMyDpOptions, IMyDateModel } from 'ngx-mydatepicker';
import { User } from '../../_models';
import { DataHubService } from '../../_services/datahub.service';
import { Commodity } from '../../_models/commodity';
import { Country } from '../../_models/country';
import { BasePeak } from '../../_models/basepeak';
import { CommodityMarkets } from '../../_models/commodityMarkets';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-data-hub',
  templateUrl: './data-hub.component.html',
  styleUrls: [
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/datahub.css'
]

})
export class DataHubComponent implements OnInit {

  datePipe: DatePipe = new DatePipe('en-US');
  currentUser: User;
  dateFrom: any = {};
  dateTo: any = {};

  btnIndex: number;
  marketCommodity: number;
  marketCountry: number;
  marketTimeperiod: number;
  marketBasepeak: number;
  marketMarket: number;

  // models
  commodities: Commodity[];
  countries: Country[];
  timePeriods: Commodity[];
  basepeaks: BasePeak[] = [];
  markets: CommodityMarkets[] = [];
  chartByMarkets: any[];

  selectedMarketsList: any  = [];
  selectedMarketObj: any = {};

  timeButtons: any = [];

  myOptions: INgxMyDpOptions = {
    dateFormat: 'dd/mm/yyyy',
    disableWeekends: true
  };

  constructor(private dataHubService: DataHubService) {
    this.currentUser = JSON.parse(localStorage.getItem('currentUser'));

    this.timeButtons = [
      {name: '7 days', id: '7D'},
      {name: '30 days', id: '30D'},
      {name: '3 Months', id: '3M'},
      {name: '6 Months', id: '6M'},
      {name: '1 Year', id: '1Y'},
      {name: '5 Year', id: '5Y'}  ];

      this.commodities = [{
              'ID': 14,
              'Name': 'Power'
          },
          {
              'ID': 1,
              'Name': 'Natural gas'
          },
          {
              'ID': 8,
              'Name': 'Oil'
          },
          {
              'ID': 2,
              'Name': 'Green'
          },
          {
              'ID': 16,
              'Name': 'Coal'
          },
          {
              'ID': 23,
              'Name': 'Economics'
          }];
  }

  ngOnInit() {
    this.changeDates('7D', 0, false);
    this.marketCommodity = 14;
    this.changeCommodity(this.marketCommodity);
  }

  onDateToChanged(event: IMyDateModel): void {
    this.dateTo = event;
  }

  onDateFromChanged(event: IMyDateModel): void {
    this.dateFrom = event;
  }

  changeDates(range: string, ind: number, toStartChart: boolean): void {
    this.btnIndex = ind;
    const date =  new Date();
    const dateCh = new Date();

    switch (range) {
      case '7D': {
          dateCh.setDate(date.getDate() - 7);
          break;
      }
      case '30D': {
          dateCh.setDate(date.getDate() - 30);
          break;
      }
      case '3M': {
          dateCh.setMonth(date.getMonth() - 3);
          break;
      }
      case '6M': {
          dateCh.setMonth(date.getMonth() - 6);
          break;
      }
      case '1Y': {
        dateCh.setMonth(date.getMonth() - 12);
        break;
      }
      case '5Y': {
        dateCh.setMonth(date.getMonth() - 60);
        break;
      }
   }

    this.dateFrom = {
      date: {
        year: dateCh.getFullYear(),
        month: dateCh.getMonth() + 1,
        day:  dateCh.getUTCDate()
      }
    };
    this.dateTo = { date: { year: date.getFullYear(), month: date.getUTCMonth() + 1, day:  date.getUTCDate() } };

    this.getChartData(toStartChart);
  }

  addNewLine(): void {
    if (this.selectedMarketsList.indexOf(this.selectedMarketObj) === -1) {
      this.selectedMarketsList.push(this.selectedMarketObj);
    }
  }

  removeSelMarket(ind: number) {
    this.selectedMarketsList.splice(ind, 1);
    this.getChartData(true);
  }

  changeCommodity(comId: number): void {
    this.dataHubService.getCountriesByCommodityId(this.marketCommodity).subscribe(
      (dataCntr: Country[]) => {
        this.countries = dataCntr;
        this.marketCountry = this.countries[0].ID;
        this.changeCountry(comId, this.countries[0].ID);
      },
      (er) => { }
    );
  }

  changeCountry(comId: number, cntrID: number): void {
    this.dataHubService.getTimePeriodsByCommodityIdCountryId(comId, cntrID).subscribe(
      (dataPeriods: Commodity[]) => {
        this.timePeriods = dataPeriods;
        this.marketTimeperiod =  this.timePeriods[0].ID;
        this.changeTimeperiod(comId, cntrID, this.timePeriods[0].ID);
      },
      (er) => { }
    );
  }

  changeTimeperiod(comId: number, cntrID: number, timeperiodId: number): void {
    this.dataHubService.getBasePeakByCommodityIdCountryIdPeriodId (
      comId,
      cntrID,
      timeperiodId).subscribe(
      (dataBP: BasePeak[]) => {
        this.basepeaks = dataBP;
        this.marketBasepeak = 1;
        const bp = this.basepeaks.length > 0 ? 1 : 0;
        this.changeBasePeak(comId, cntrID, timeperiodId, bp);
      },
      (er) => { }
    );

  }

  changeBasePeak(comId: number, cntrID: number, timeperiodId: number, basePeakId: number): void {
    this.dataHubService.getMarketsByCommodityIdCountryIdPeriodId(
      comId,
      cntrID,
      timeperiodId,
      basePeakId
    ).subscribe(
      (dataMrkt: CommodityMarkets[]) => {
        this.markets = dataMrkt;
        this.marketMarket = this.markets[0].Market_ID;
        this.selectedMarketObj = {
          market_id: this.markets[0].Market_ID,
          market_name: this.markets[0].Market_Name
        };
      },
      (er) => { }
    );
  }

  // get data; generate chart;
  marketChange(args: any, val: number): void {
    this.selectedMarketObj = {
      market_id: val,
      market_name: args.target.options[args.target.selectedIndex].text
    };
  }

  getChartData(toStartChart: boolean): void {
    if (toStartChart) {
        this.chartByMarkets = null;
        const tobj: any = {};
        tobj.MarketID =  this.selectedMarketsList.map((ob: any) => {
          return ob.market_id;
        });

        tobj.MarketID.push(this.marketMarket);
        tobj.DateStart = this.datePipe.transform(new Date(this.dateFrom.date.year, this.dateFrom.date.month - 1, this.dateFrom.date.day),
        'yyyy-MM-dd');
        tobj.DateEnd = this.datePipe.transform(new Date(this.dateTo.date.year, this.dateTo.date.month - 1, this.dateTo.date.day),
        'yyyy-MM-dd');

        this.dataHubService.getChartData(tobj).subscribe(
          (chartData: any[]) => {
            this.chartByMarkets = chartData;
          },
          (er) => { }
        );
    }
  }

}
