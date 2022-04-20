import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Chart } from 'angular-highcharts';
import * as Highcharts from 'highcharts';
import { Observable } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { SharableService } from '../../_services/sharable.service';

@Component({
  selector: 'app-hedge-div',
  templateUrl: './hedge-div.component.html',
  styleUrls: ['./hedge-div.component.css']
})
export class HedgeDivComponent implements OnInit {

  constructor(private http: HttpClient, private vano: SharableService) { }

  results: any;
  chart: Chart[] = new Array<Chart>();
  empty: any = true;
  active: any;
  acolor: any;
  sdelete: boolean;
  colors: string[] = ['#ffffff', '#37475a'];
  co: number;
  colorbg = '#ffffff';
  colorf = '#37475a';
  hr = 'Hedge Reporting';
  vanoo: any;



  ngOnInit() {
        this.active = false;
        this.http.get('http://www.marketpricesolutions.com/apitest.asp?act=gethedgedata&cid=1533').subscribe(data => {

            this.results = data;

            if ( $.isEmptyObject(data) ) { this.empty = false; }

            this.co = 3;

            this.vano.active.subscribe(acolor => this.acolor = acolor);
            this.vano.adel.subscribe(sdelete => this.sdelete = sdelete);

            this.vano.colorBg3.subscribe(bgc => this.colors[0] = bgc);
            this.vano.colorFont3.subscribe(fc => this.colors[1] = fc);

            this.vano.colorbg.subscribe(bgc => this.colorbg = bgc);
            this.vano.colorf.subscribe(fc => this.colorf = fc);

            let i = 0;

            this.results.forEach(kek => {
                this.chart[i] = new Chart(<any>{
                      chart: {
                          plotBackgroundColor: null,
                          plotBorderWidth: 0,
                          type: 'solidgauge',
                          margin: [0, 0, 0, 0],
                          backgroundColor: 'transparent',
                          plotShadow: false
                      },
                      exporting: { enabled: false },
                      credits: {enabled: false},
                      title: {
                          // tslint:disable-next-line:radix
                          text: parseInt(kek['fixed']) + '%',
                          align: 'center',
                          verticalAlign: 'middle',
                          y: 8,
                          style: {
                                      fontWeight: 'bold',
                                      fontSize: '29px',
                                      color: 'white',
                                      fontFamily: 'Open Sans, sans-serif'
                                  }
                      },
                      yAxis: {
                                labels: {
                                        enabled: false
                                 },
                                min: 0,
                                max: 100,
                                lineWidth: 0,
                                tickWidth: 0,
                                minorTickLength: 0
                      },
                      tooltip: {
                          pointFormat: `{series.name}: <b>{point.y:.2f}%</b>`
                      },
                      pane: {
                           size: '65%',
                           center: ['50%', '50%'],
                           startAngle: 0,
                           endAngle: 360,
                           background: {
                           borderWidth: 0,
                           backgroundColor: '#37475a',
                           shape: 'arc',
                               outerRadius: '0%',
                               innerRadius: '80%'
                           }
                       },
                      plotOptions: {
                           solidgauge: {
                              borderColor: '#ffa82c',
                              borderWidth: 12,
                              radius: 90,
                              innerRadius: '90%',
                              dataLabels: {
                                          y: 60,
                                          borderWidth: 0,
                                          useHTML: true,
                                          format: `<b></b>`
                              }
                          }
                      },
                      series: [{
                          type: `solidgauge`,
                          name: `Fixed`,
                          // tslint:disable-next-line:radix
                          data: [parseInt(kek['fixed'])]
                 }]
                });

                i++;

});

});

}


  verify() {
    if (this.hr.length < 4) { this.hr = 'Hedge Reporting'; }
  }

  offMe() {
    this.vano.changeActive(this.acolor);
    this.vano.changeCO(3);
    this.colorbg = this.colors[0];
    this.colorf = this.colors[1];
    this.vano.changeAuxColorBg(this.colorbg);
    this.vano.changeAuxColorF(this.colorf);
  }
  offMee() {
    this.vano.changeDel(this.sdelete);
  }



}
