import { Component, OnInit } from '@angular/core';
import { Chart } from 'angular-highcharts';

@Component({
  selector: 'app-anl-interet-bar-chart',
  templateUrl: './anl-interet-bar-chart.component.html',
})
export class AnlInteretBarChartComponent implements OnInit {

  chart: Chart;

  constructor() { }

  ngOnInit() {
    const data = [33, 45, 38, 59, 25];
    this.chart = new Chart({
      legend: { enabled: false },
      chart: {
          type: 'column'
      },
      title: {
          text: 'Intérêt par catégorie',
          align: 'left',
          margin: 35,
          style: {
              color: '#484848',

          }
      },
      xAxis: {
          categories: ['Gaz Naturel', 'Petrole', 'Electricite', 'Renouvelable', 'Nucleaire'],
          lineColor: '#A9A9A9',
      },
      yAxis: {
          tickInterval: 15,
          max: 60,
          title: {
              text: ''
          },
          gridLineColor: '#A9A9A9',
          gridLineWidth: 1.5
      },
      plotOptions: {
          column: {
              pointPadding: 0,
              groupPadding: 0.25,
              colorByPoint: true,

          }
      },
      colors: [
          '#ff9966',
          '#ff6666',
          '#d279a6',
          '#993366',
          '#732673'
      ],
      series: [{ data: data },
      ]
    });
  }

}
