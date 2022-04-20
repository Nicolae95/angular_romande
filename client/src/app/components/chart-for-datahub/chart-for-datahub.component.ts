import { Component, OnInit, Input, OnDestroy } from '@angular/core';
import { Chart } from 'angular-highcharts';
import { forEach } from '@angular/router/src/utils/collection';
import * as moment from 'moment';
import { IfObservable } from 'rxjs/observable/IfObservable';

@Component({
  selector: 'app-chart-for-datahub',
  templateUrl: './chart-for-datahub.component.html'
})
export class ChartForDatahubComponent implements OnInit, OnDestroy {
  @Input() data: any;
  chart: Chart;
  series: any[] = [];
  YAxis: any[] = [];
  rawYAxys: any[] = [];
  chartColors: string[];
  lineColors: string[] = [];

  constructor() {
    this.chartColors = ['#4572A7', '#AB4744', '#89A54E', '#80699B', '#E46C0A', '#FCEE06'];
    this.lineColors.push('#4572A7');
  }

  ngOnInit() {
    let tobj = [], arr = [], dt;

    // Checking the currencies and unit values
    this.data.forEach((element, key)  => {
      this.rawYAxys.push(
        {'curr':  element.Market.Currency_Name,
        'unit': element.Market.Unit_Name
      });
    });

    // Remove duplicate objects
    const rY = this.filterArr(this.rawYAxys);

  // Generating data lines
  this.data.forEach((element, key)  => {
      arr = element.Data.map((ob: any) => {
        tobj  = [];
        dt    = new Date(ob.Market_Date);
        tobj.push(Date.UTC(dt.getFullYear(), dt.getMonth(), dt.getDate()));
        tobj.push(ob.Market_Value);
        return tobj;
      });

      if (element.Market.Currency_Name.toLowerCase() === rY[0].curr.toLowerCase()
      && element.Market.Unit_Name.toLowerCase() === rY[0].unit.toLowerCase()) {
        this.series.push({name: element.Market.Market_Name, data: arr});
      } else {
        this.series.push({name: element.Market.Market_Name, data: arr, yAxis: 1});
        this.lineColors.push(this.chartColors[key]);
      }
    });

    // Generting YAxe(s)
    rY.forEach((obj, key) => {
         this.YAxis.push({
           minorTickInterval: 'auto',
           tickWidth: 1,
           gridLineWidth: 1,
           labels: {style: {color: this.lineColors[key]}},
           title: {
             text:  obj.curr + '/' + obj.unit,
             style: {color: this.lineColors[key]}
           }});

          if (key === 1) {
           this.YAxis[this.YAxis.length - 1].opposite = true;
         }
    });
    this.generateChart(this.YAxis.length);
  }


  generateChart(multiY: number): void {
    let localY = null;
    if (multiY > 1) {
      localY = this.YAxis;
    } else {
      localY = this.YAxis[0];
    }
    this.chart = new Chart({
      chart: {
        height: 500,
        zoomType: 'x',
        borderColor: '#fff',
        borderRadius: 0,
        plotBorderColor: '#ededed',
        plotBorderWidth: 1,
        borderWidth: 2,
        defaultSeriesType: 'line'
      },
      title: {
          text: ''
      },
      subtitle: {
          text: ''
      },
    colors: this.chartColors,
    xAxis: {
        gridLineWidth: 1,
        lineColor: '#000',
        tickColor: '#000',
        type: 'datetime',
        maxZoom: 7 * 24 * 3600000
      },
      tooltip: {
        xDateFormat: '%B %e, %Y %H:00',
        useHTML: true,
        borderWidth: 0,
        valueDecimals: 2,
        headerFormat: '<b>{series.name}</b><table><tr><td>Date: </td><td>{point.key}</td></tr>',
        pointFormat: '<tr><td>Value:&nbsp;</td><td style="text-align:left">{point.y}</b></td></tr>' +
        '<tr><td colspan="2" style="text-align:left;">{point.id}</b></td></tr>',
        footerFormat: '</table>'
      },
      plotOptions: {
        line: { lineWidth: 2, states: {hover: {lineWidth: 2}},
            marker: {
              enabled: false,
              states: {hover: {enabled: true, radius: 5, lineWidth: 1 }}
            }
        }
      },
      yAxis: localY,
      series: this.series
    });
  }

// ==============================================================
  filterArr(arr: any[]): any[] {
    const filteredArr: any = [];
    let exists: boolean;
    arr.forEach(obj => {
      exists = false;
      filteredArr.forEach(obj2 => {
       if (obj.curr === obj2.curr || obj.unit === obj2.unit) { exists = true; }
     });
     if (exists === false && obj.id !== '') { filteredArr.push(obj); }
    });
    return filteredArr;
  }

  ngOnDestroy() {
    delete this.series;
    delete this.data;
  }
}


