import { Component, OnInit, Input } from '@angular/core';
import { Chart } from 'angular-highcharts';
import { forEach } from '@angular/router/src/utils/collection';
import * as moment from 'moment';

@Component({
  selector: 'app-char-by-years',
  templateUrl: './char-by-years.component.html',
})
export class CharByYearsComponent implements OnInit {

 @Input() data: any;
  chart: Chart;
  dataInChart: any;
  tikc: any;
  positions: any;
  series: any[] = [];
  yearList: any[] = [];
  year: any;
  show = false;

  constructor() { }
  ngOnInit() {
        this.data.years.forEach(element => {
        for (const key in this.data.history) {
            if (this.data.history.hasOwnProperty(key)) {
            const i = this.data.history[key];
                if (this.data.history[key].length > 1) {
                    this.show = true;
                    if ( key === String(element)) { this.series.push( {name: key, data: this.data.history[key] }, ); }
                } else { this.show = false; }
            }
        }
        });


    this.chart = new Chart({
      chart: {
        type: 'line',
        height: 330,
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
                fontFamily: 'Open Sans, sans-serif'
            }
        }
    },
      yAxis: {
          title: {
              text: 'ct. CHF/kWh'
          }
      },
      plotOptions: {
          line: {
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
