import { Input, Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { SharableService, CockpitBService } from '../../_services';
import { ActivatedRoute } from '@angular/router';

const httpOptions = {
        headers: new HttpHeaders({ 'Content-Type': 'application/json' })
      };


@Component({
  selector: 'app-stats-div',
  templateUrl: './stats-div.component.html',
  styleUrls: ['./stats-div.component.css']
})

export class StatsDivComponent implements OnInit {

@Input() check: any;
@Input() id: any;

  testme: string[];
  order: string;
  wday: string;
  wdate: string;
  active: boolean;
  acolor: boolean;
  sdelete: boolean;
  editn: any;
  action: any;
  enrglist: string[] = ['power', 'gas', 'coal', 'emissions', 'oil', 'rates', 'others'];
  uid: any = 0;
  auxstring: string[] = [];
  colors: string[] = ['#ffffff', '#37475a'];
  co: number;
  colorbg = '#ffffff';
  colorf = '#37475a';
  stats = 'Statistics';
  // id: number;
  chartByMarkets: any;

  constructor(private http: HttpClient,
              private sharableService: SharableService,
              private cockpitBService: CockpitBService,
              private activatedRoute: ActivatedRoute
              ) {
                // this.activatedRoute.params.subscribe( params =>  {this.id = params.id; });
              }

  ngOnInit() {
    this.chartsByCockpit(this.id);
    // getForTables
      // this.http.get('http://www.marketpricesolutions.com/apitest.asp?act=datafortable&cid=1533').subscribe(data => {


    // this.active = false;
    // this.sharableService.active.subscribe(acolor => this.acolor = acolor);
    // this.sharableService.adel.subscribe(sdelete => this.sdelete = sdelete);

    // this.sharableService.colorBg1.subscribe(bgc => this.colors[0] = bgc);
    // this.sharableService.colorFont1.subscribe(fc => this.colors[1] = fc);

    // this.sharableService.colorbg.subscribe(bgc => this.colorbg = bgc);
    // this.sharableService.colorf.subscribe(fc => this.colorf = fc);
  }

  getInEMP_tables(ids: any) {
    ids = ids.filter((el, i, a) => i === a.indexOf(el));

    this.cockpitBService.getForTables(ids).subscribe(data => {
      this.testme = data['data'];
      this.order = data['orderby'];
      this.wday = data['days']['wday'].split(',');
      this.wdate = data['days']['wdate'].split(',');
      this.co = 1;
      data['data'].forEach(x => {
        if (x.uid > this.uid) {
          this.uid = x.uid;
          this.auxstring.push(x.uid);
        }
      });
    });
  }


  chartsByCockpit(id: number) {
    this.cockpitBService.getChartsByCockpit(id).subscribe(
      (data) => {
        const market_id = [];
        // console.log('data', data);
        for (const key in data) {
          if (data.hasOwnProperty(key)) {
            const mark = data[key];
            mark.ids = [];
            // console.log('mark', mark);
            if (mark.tabel === true) {
                mark.markets.forEach(e => {
                  mark.ids.push(e.market_id);
                });
            }

          }
        }
        // for (const key in data) {
        //   if (data.hasOwnProperty(key)) {
        //     const mark = data[key];
        //     if (mark.ids.length !== 0) {
        //       this.getChartData(true, mark.ids, Number(key));
        //     }
        //   }
        // }

        this.chartByMarkets = data;
        const id_alls = [];
        this.chartByMarkets.forEach((e, index) => {
          e.ids = e.ids.filter((el, i, a) => i === a.indexOf(el));
          if ( e.ids.length !== 0) { e.ids.forEach(ids => { id_alls.push(ids); }); }
        });

        if ( id_alls.length !== 0) { this.getInEMP_tables(id_alls); }

      },
      (er) => {},
    );
  }

  filterOf(nr: number) {
    return this.testme.filter(x => x['uid'] === nr);
  }

  verify() {
    if (this.stats.length < 4) { this.stats = 'Statistics'; }
  }

  offMe() {
    this.sharableService.changeActive(this.acolor);
    this.sharableService.changeCO(1);
    this.colorbg = this.colors[0];
    this.colorf = this.colors[1];
    this.sharableService.changeAuxColorBg(this.colorbg);
    this.sharableService.changeAuxColorF(this.colorf);
  }
  offMee() {
    this.sharableService.changeDel(this.sdelete);
  }

onSubmit() {
  return this.http.post('http://www.marketpricesolutions.com/apitest.asp', this.editn, httpOptions).
  subscribe(data => {alert(data); },
     error => {alert('Error'); }
    );
  }

  GiveClass(i: any): string {
    if ( i > 0 ) {
      return 'bgpink';
    } else {
    if (i === 0) {
    return '';
    } else { return 'bggoluboi'; }
      }
  }

}
