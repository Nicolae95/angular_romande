import { Component, OnInit, Input } from '@angular/core';
import { Chart } from 'angular-highcharts';
import { forEach } from '@angular/router/src/utils/collection';
import * as moment from 'moment';


@Component({
  selector: 'app-chart-cc-weekly',
  templateUrl: './chart-cc-weekly.component.html',
})
export class ChartCcWeeklyComponent implements OnInit {
  @Input() data: any;
  chart: Chart;
  dataTempor: any;

  constructor() { }

  ngOnInit() {
    this.chart = new Chart({
      chart: {
        type: 'spline',
        // scrollablePlotArea: {
        //     minWidth: 600,
        //     scrollPositionX: 1
        // }
      },

      title: {
          text: 'CC horaire'
      },
      subtitle: {
          text: ''
      },
      xAxis: {
        categories: [],
        tickPositioner: function () {
             this.positions = [],
             this.tick = Math.floor(this.dataMin + 1);
             while (this.tick < this.dataMax) {
                 this.positions.push(this.tick);
                 this.tick += 4;
             }
             this.positions.push(this.dataMax);
             return this.positions;
         },
      },
      yAxis: {
          title: {
              text: 'kWh'
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
      series: [
        {name: 'CC horaire', data: this.data.records, color: '#e05d76'},
      ]
    });

  }
}
