import { Component, OnInit, Input } from '@angular/core';
import { Chart } from 'angular-highcharts';


@Component({
  selector: 'app-weekly-chart',
  templateUrl: './weekly-chart.component.html',
})

export class WeeklyChartComponent implements OnInit {
 @Input() data: any;
  chart: Chart;
  dataTempor: any;
  tikc: any;
  positions: any;


  ngOnInit() {


         let dates = [];
         if (this.data.hedges_diagram.length !== 0) {
              dates =   [{name: 'Achats marché', data: this.data.hedges_diagram, color: '#a6a6a6' },
                         {name: 'CC horaire',    data: this.data.weekly_value,    color: '#e05d76'}];
         } else { dates = [ {name: 'CC horaire',    data: this.data.weekly_value,  color: '#e05d76'}]; }

        this.chart = new Chart({
        chart: {
            type: 'spline',
            width: 907,
        },
        title: {
            text: 'Profil hebdomadaire du client'
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
                        this.tick += 6;
                    }
                    this.positions.push(this.dataMax);
                    return this.positions;
                },
            },
        yAxis: {
            title: {
                text: 'MWh'
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
        series: dates
        });

    }

}
