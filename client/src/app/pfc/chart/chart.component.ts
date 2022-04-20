import { Component, OnInit, Input } from '@angular/core';
import { Chart } from 'angular-highcharts';
import { forEach } from '@angular/router/src/utils/collection';

@Component({
  selector: 'app-chart',
  templateUrl: './chart.component.html',
})

export class ChartComponent implements OnInit {
  @Input() data: any;
  @Input() valute: string;
  chart: Chart;

  ngOnInit() {

    this.chart = new Chart({
      chart: {
          zoomType: 'x',
      },
      title: {
          text: this.data.data + ' data'
      },
      subtitle: {
        text: document.ontouchstart === undefined ?
            'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
      },
      xAxis: {
          type: 'datetime'
      },
      yAxis: {
          title: {
            //   text: this.data.data
            text: this.valute
          }
      },
      legend: {
          enabled: false
      },
      series: [{
        name: this.data.data + ' value',
        data: this.data.records
      }]
    });

  }

}


