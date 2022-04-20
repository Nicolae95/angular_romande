import { Component, OnInit, Input } from '@angular/core';
import { Chart } from 'angular-highcharts';
import { forEach } from '@angular/router/src/utils/collection';
import * as moment from 'moment';


@Component({
  selector: 'app-season-chart',
  templateUrl: './season-chart.component.html',
})
export class SeasonChartComponent implements OnInit {
 @Input() data: any;
  chart: Chart;
  dataTempor: any;
  constructor() { }

  ngOnInit() {
    this.chart = new Chart({
      chart: {
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        type: 'pie'
      },
      title: {
        text: 'Répartition consommation'
      },
      tooltip: {
        pointFormat: '{series.name}: <b>{point.percentage:.2f}%</b>'
      },
      plotOptions: {
          pie: {
              allowPointSelect: true,
              cursor: 'pointer',
              dataLabels: {
                  enabled: true,
                  format: '<b>{point.name}</b><br>{point.percentage:.2f} %',
                  distance: -50,
                  style: {}
              }
          },



      },
      series: [{
        name: 'Consommation',
        data: [
          {name: 'Hiver HP', y: this.data[0]['value'], color: '#d9d9d9' },
          {name: 'Hiver HC', y: this.data[2]['value'], color: '#f2f2f2' },
          {name: 'Eté HP',   y: this.data[1]['value'], color: '#ffd966' },
          {name: 'Eté HC',   y: this.data[3]['value'], color: '#fff2cc' },
        ]
    }]
    });
  }

}


