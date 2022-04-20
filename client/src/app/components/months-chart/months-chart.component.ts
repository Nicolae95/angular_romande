import { Component, OnInit, Input } from '@angular/core';
import { Chart } from 'angular-highcharts';
import { forEach } from '@angular/router/src/utils/collection';
import * as moment from 'moment';


@Component({
  selector: 'app-months-chart',
  templateUrl: './months-chart.component.html',
})
export class MonthsChartComponent implements OnInit {
 @Input() data: any;
  chart: Chart;
  dataTempor: any;
  constructor() { }

  ngOnInit() {
    // this.months();
    this.chart = new Chart({
      chart: {
        type: 'column'
      },
      plotOptions: {
        column: {
            colorByPoint: true
        }
      },
      colors: ['#959090', '#959090', '#959090', '#ffd966', '#ffd966', '#ffd966', '#ffd966',  '#ffd966', '#ffd966'],
      title: {
        text: 'Consommations mensuelles'
      },
      // subtitle: {
      //   text: document.ontouchstart === undefined ?
      //   'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
      // },
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
          min: 0,
          title: { text: 'MWh' }
      },
      legend: {
          enabled: false
      },
      tooltip: {
        pointFormat: 'Consommation: <b>{point.y:.1f} </b>'
    },
      series: [
        {name: 'Month diagram', data: this.data},
        // , color: this.series.index === 1 ? 'red' : 'green'
      ]
    });
  }

  months() {
    this.dataTempor = this.data;
    this.data = [];
    this.dataTempor.forEach(element => {
      // if (element[0] < 4 && element[0] > 8) {
        this.data.push([moment.months(element[0] - 1), element[1]]);
      // } else { this.data.push([moment.months(element[0] - 1), element[1] , '#00ff00']);  }

    });
  }

}


