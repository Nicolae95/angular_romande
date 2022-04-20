import { Component, OnInit, Input } from '@angular/core';
import { Chart } from 'angular-highcharts';
import { forEach } from '@angular/router/src/utils/collection';
import * as moment from 'moment';


@Component({
  selector: 'app-risque-chart',
  templateUrl: './risque-chart.component.html',
})
export class RisqueChartComponent implements OnInit {

    @Input() data: any;
    @Input() type: number;

    chart: Chart;
    dataInChart: any;
    tikc: any;
    positions: any;
    series: any[];


  constructor() { }

  ngOnInit() {

    switch (this.type) {
        case 1: {
            this.series = [
                {name: 'Risque PwB', data: this.data.records['Risque PwB'], color: '#ffa500' },
                {name: 'Risque prix', data: this.data.records['Risque prix'], color: '#ef2e2e' },
                {name: 'Risque volume', data: this.data.records['Risque volume'], color: '#ccc' },
            ];
            break;
        }
        case 2: {
            this.series = [
                {name: 'Mix hydro-solaire suisse', data: this.data.records['Mix hydro-solaire suisse'], color: '#ffa500' },
                {name: 'Hydro Naturemade Star suisse', data: this.data.records['Hydro Naturemade Star suisse'], color: '#ef2e2e' },
                {name: 'Nucléaire suisse', data: this.data.records['Nucléaire suisse'], color: '#ccc' },
                {name: 'Hydro européens', data: this.data.records['Hydro européens'], color: '#4572A7' },
                {name: 'Hydro suisse', data: this.data.records['Hydro suisse'], color: '#AB4744' },
                {name: 'Hydro Naturemade Star romand', data: this.data.records['Hydro Naturemade Star romand'], color: '#89A54E' }
            ];
            break;
        }
    }

    this.chart = new Chart({
      chart: {
        type: 'line',
        height: 330
      },
      title: {
          text: ''
      },
      subtitle: {
          text: ''
      },

    xAxis: {
        type: 'category',
        labels: {
            rotation: -45,
            style: {
                fontSize: '13px',
                fontFamily: 'Verdana, sans-serif'
            }
        }
    },
      yAxis: {
          title: {
              text: 'ct/kWh'
          }
      },
      plotOptions: {
          spline: {
            enableMouseTracking: true,
            lineWidth: 2,
            states: {
                hover: {
                    lineWidth: 3
                },

            },
            marker: {
                enabled: false
            },
            // step: true,

        },
        pie: {
            color: {},
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
              enabled: false
            },
            showInLegend: true
          }
        },
        series: this.series
    });
  }

}
