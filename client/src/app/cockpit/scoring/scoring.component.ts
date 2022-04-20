import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { SharableService } from '../../_services';

@Component({
  selector: 'app-scoring',
  templateUrl: './scoring.component.html',
  styleUrls: ['./scoring.component.css']
})
export class ScoringComponent implements OnInit {

  constructor(private http: HttpClient, private vano: SharableService) { }

  results: any;
  empty: any = true;
  active: any;
  acolor: any;
  sdelete: boolean;
  colors: string[] = ['#ffffff', '#37475a'];
  co: number;
  colorbg = '#ffffff';
  colorf = '#37475a';
  score = 'Procurement Scoring';


  ngOnInit() {
  this.http.get('http://www.marketpricesolutions.com/apitest.asp?act=getscoringdata&cid=1533').subscribe(data => {

        this.results = data;
        this.co = 4;

        if ( $.isEmptyObject(data) ) { this.empty = false; }

        this.vano.active.subscribe(acolor => this.acolor = acolor);
        this.vano.adel.subscribe(sdelete => this.sdelete = sdelete);

        this.vano.colorBg4.subscribe(bgc => this.colors[0] = bgc);
        this.vano.colorFont4.subscribe(fc => this.colors[1] = fc);

        this.vano.colorbg.subscribe(bgc => this.colorbg = bgc);
        this.vano.colorf.subscribe(fc => this.colorf = fc);
    });

  // }

}


  verify() {
    if (this.score.length < 4) { this.score = 'Procurement Scoring'; }
  }

  offMe() {
    this.vano.changeActive(this.acolor);
    this.vano.changeCO(4);
    this.colorbg = this.colors[0];
    this.colorf = this.colors[1];
    this.vano.changeAuxColorBg(this.colorbg);
    this.vano.changeAuxColorF(this.colorf);
  }
  offMee() {
    this.vano.changeDel(this.sdelete);
  }
}
