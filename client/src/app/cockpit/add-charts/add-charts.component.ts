import { Component, OnInit } from '@angular/core';
import { INgxMyDpOptions, IMyDateModel } from 'ngx-mydatepicker';
import { User } from '../../_models';
import { DataHubService } from '../../_services/datahub.service';
import { Commodity } from '../../_models/commodity';
import { Country } from '../../_models/country';
import { BasePeak } from '../../_models/basepeak';
import { CommodityMarkets } from '../../_models/commodityMarkets';
import { DatePipe } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { CockpitService } from '../../_services/cockpit.service';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-add-charts',
  templateUrl: './add-charts.component.html',
  styleUrls: [
    // '../../../assets/css/styles/cockpitB.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/theme.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/datahub.css'
]
})
export class AddChartsComponent implements OnInit {
  id: number;
  cockpit: any;
  nameMenu = 'general';
  contenTab = 'manag';
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

  cockpitCharts: any;

  selectedMarketsList: any  = [];
  selectedMarketObj: any = {};

  timeButtons: any = [];
  nameChart: string;
  categoryName: any;
  // marketsID = [];
  sub = false;
  marketsIDS = [];


  myOptions: INgxMyDpOptions = {
    dateFormat: 'dd/mm/yyyy',
    disableWeekends: true
  };
  addChat = false;
  chart =   false;
  chartId = 'nimic';
  table =   false;


  constructor(private activatedRoute: ActivatedRoute,
              private router: Router,
              private cockpitService: CockpitService,
              private dataHubService: DataHubService,
              private toastr: ToastrService) {
    this.activatedRoute.params.subscribe( params =>  {this.id = params.id; });
    this.currentUser = JSON.parse(localStorage.getItem('currentUser'));
    this.timeButtons = [
      {name: '7 days',   id: '7D'},
      {name: '30 days',  id: '30D'},
      {name: '3 Months', id: '3M'},
      {name: '6 Months', id: '6M'},
      {name: '1 Year',   id: '1Y'},
      {name: '5 Year',   id: '5Y'}
    ];

      this.commodities = [
        {'ID': 14, 'Name': 'Power' },
        {'ID': 1,  'Name': 'Natural gas' },
        {'ID': 8,  'Name': 'Oil' },
        {'ID': 2,  'Name': 'Green' },
        {'ID': 16, 'Name': 'Coal' },
        {'ID': 23, 'Name': 'Economics'
          }];
  }

  ngOnInit() {
    this.changeDates('7D', 0, false);
    this.marketCommodity = 14;
    this.changeCommodity(this.marketCommodity);
    if (this.id) { this.getcockpit(this.id);  this.getExistingChart(this.id); }
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
      case '7D':  { dateCh.setDate(date.getDate() - 7); break; }
      case '30D': { dateCh.setDate(date.getDate() - 30); break; }
      case '3M':  { dateCh.setMonth(date.getMonth() - 3); break; }
      case '6M':  { dateCh.setMonth(date.getMonth() - 6); break; }
      case '1Y':  { dateCh.setMonth(date.getMonth() - 12); break; }
      case '5Y':  { dateCh.setMonth(date.getMonth() - 60); break; }
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
    // this.getChartData(true);
    if (this.selectedMarketsList.indexOf(this.selectedMarketObj) === -1) {
      switch (this.marketCommodity) {
        case 14:  { this.getCategoryName('Power');       break; }
        case 1:   { this.getCategoryName('Natural gas'); break; }
        case 8:   { this.getCategoryName('Oil');         break; }
        case 2:   { this.getCategoryName('Green');       break; }
        case 16:  { this.getCategoryName('Coal');        break; }
        case 23:  { this.getCategoryName('Economics');   break; }
     }

    }
  }


  getCategoryName(name: any) {
      this.cockpitService.getCategoryName(name).subscribe(
        (data) => {
          this.categoryName = data;
          // this.marketsID.push(data['id']);
          // this.selectedMarketObj.id = data['id'];
          // this.selectedMarketsList.push(this.selectedMarketObj);
          this.addMarket(data['id']);
        },
        (er) => { }
      );
  }
  name(name: string) {
    this.sub = false;
    if (this.nameChart !== '') { this.sub = true; }
  }

  ch(ev: any) { this.chart = false;  this.table = false; }

  addMarket(id: number) {

    let market = {};
    try {
        market = {
          category: id,
          name: this.chartByMarkets[this.chartByMarkets.length - 1]['Market'].Market_Name,
          market_id: this.chartByMarkets[this.chartByMarkets.length - 1]['Market'].Market_ID,
          currency: this.chartByMarkets[this.chartByMarkets.length - 1]['Market'].Currency_Name,
          description: this.chartByMarkets[this.chartByMarkets.length - 1]['Market'].Market_Description,
          unit: this.chartByMarkets[this.chartByMarkets.length - 1]['Market'].Unit_Name,
     };
    } catch (error) { setTimeout(() => { this.getChartData(true); }, 5000);  }



    this.cockpitService.putCockpitMarket(market).subscribe(
      (data) => {
      //  this.marketsIDS.push(data['id']);
       this.selectedMarketObj.id = data['id'];
       this.selectedMarketsList.push(this.selectedMarketObj);
      },
      (er) => { },
    );

  }
  removeSelMarket(sml: any, y: any) {
    this.cockpitService.deleteCockpitMarket(sml.id).subscribe(
      (data) => {
        //  this.chartByMarkets = this.chartByMarkets.filter(x => x.Market.Market_ID !== sml.market_id);
        this.selectedMarketsList.splice(y, 1);
        if (this.selectedMarketsList.length !== 0) {
          this.getChartData(true, false);
        } else { this.chartByMarkets = null; }

      },
      (er) => {},
    );

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

  getChartData(toStartChart: boolean, addNewLine?: boolean): void {
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

        // console.log('getChartData', tobj);
        this.dataHubService.getChartData(tobj).subscribe(
          (chartData: any[]) => { this.chartByMarkets = chartData; if (addNewLine === true) { this.addNewLine(); } },
          (er) => { }
        );
    }
  }

  getcockpit(id: number) {
    this.cockpitService.getCockpitNewsById(Number(this.id)).subscribe(
      (data) => { this.cockpit = data; },
      (er) => { this.router.navigate(['/cockpit']); }
    );
  }

  getExistingChart(id: number) {
    this.cockpitService.getCockpitsById(Number(this.id)).subscribe(
      (data) => { this.cockpitCharts = data; },
      (er) => { }
    );
  }

  putCockpit (cockpit: any) {
    // 'name', 'category', 'market_id', 'currency', 'description', 'unit'
    this.cockpitService.putCockpitMarket(cockpit).subscribe(
    );
  }

  addChartMarket() {
    const ids = [];
    this.selectedMarketsList.forEach(e => { ids.push(e.id); });

    const chartMarket = {
      name: this.nameChart,
      cockpit: Number(this.id),
      markets: ids,
      tabel: Boolean(this.table),
      chart: Boolean(this.chart),
    };
    // console.log('chartMarket', chartMarket);
    if (Boolean(this.chart) ===  true) { // new
        this.cockpitService.add_New_ChartMarket(chartMarket).subscribe(
          data => {
             this.toastr.success('Le market a été ajouté');
            this.router.navigate(['/cockpits/list']);
           },
          er => {  },
        );
    } else { // existing
      this.cockpitService.add_to_existent_ChartMarket(this.chartId, chartMarket).subscribe(
        data => {
           this.toastr.success('Le market a été ajouté');
          this.router.navigate(['/cockpits/list']);
         },
        er => { },
      );
    }

  }

  putChartWidhtMarket() { }

}
