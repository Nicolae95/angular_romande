import { Component, OnInit, Input } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map, tap } from 'rxjs/operators';
import { SharableService } from '../../_services';
import { News, NewsForm } from '../../_models';

@Component({
  selector: 'app-news-div',
  templateUrl: './news-div.component.html',
  styleUrls: ['./news-div.component.css']
})

export class NewsDivComponent implements OnInit {
results:  any;
text: string[];
stiri:  News;
img:  string;
title: string;
active:  boolean;
editn:  NewsForm;
clist:  string[];
acolor: boolean;
sdelete: boolean;
action:  any;
maindata:  any;
colors:  string[] = ['#ffffff',  '#37475a'];
co: number;
colorbg = '#ffffff';
colorf = '#37475a';

constructor(private http: HttpClient, private vano: SharableService) { }

    ngOnInit() {
        this.active = false;
        this.clist = ['All categories', 'Daily', 'Oil', 'Natural Gas', 'Power', 'Energy', 'Nuclear', 'Coal', 'Economics', 'Renewables'];
        this.editn = new NewsForm (1, 'Market News',  4, [false, false, false, false, false, false, false, false, false, false]);

        this.vano.active.subscribe(acolor => this.acolor = acolor);
        this.vano.adel.subscribe(sdelete => this.sdelete = sdelete);

        this.vano.colorBg.subscribe(bgc => this.colors[0] = bgc);
        this.vano.colorFont.subscribe(fc => this.colors[1] = fc);

        this.vano.colorbg.subscribe(bgc => this.colorbg = bgc);
        this.vano.colorf.subscribe(fc => this.colorf = fc);

        this.vano.co.subscribe(co => this.co = co);
        this.co = 0;

        this.http.get('http://149.56.102.173:80/api/v1/latest/validated/').subscribe(data => {
        this.maindata = data;
        console.log(this.maindata);
        this.results = this.maindata.slice(0, 4);
    });

    }

    closeall() {
        this.active = false;
        this.vano.changeActive(false);
        this.vano.changeDel(false);
    }

    filterMe() {
        if (this.editn.categories[0]) { console.log('all categories'); }
        if (this.editn.categories[1]) { console.log('daily'); }
        if (this.editn.categories[2]) { console.log('oil'); }
        if (this.editn.categories[3]) { console.log('natural gas'); }
        if (this.editn.categories[4]) { console.log('power'); }
        if (this.editn.categories[5]) { console.log('energy'); }
        if (this.editn.categories[6]) { console.log('nuclear'); }
        if (this.editn.categories[7]) { console.log('coal'); }
        if (this.editn.categories[8]) { console.log('economics'); }
        if (this.editn.categories[9]) { console.log('renewables'); }
    }
    setNews() {
        this.results = this.maindata.slice(0, this.editn.numberof);
    }

    filterNews() {
        console.log(this.results);
    }

    offMe() {
        this.vano.changeActive(this.acolor);
        this.vano.changeCO(0);
        this.colorbg = this.colors[0];
        this.colorf = this.colors[1];
    }

  verify() {
    if (this.editn.name.length < 4) { this.editn.name = 'Market News'; }
  }

    offMee() {
        this.vano.changeDel(this.sdelete);
    }

    ShowMe(id: News): void {
        this.stiri = {
            title: id['title'],
            id: id['id'],
            created: id['created'],
            source: id['source']['title'],
            validated_text : id['validated_text']
        };
    }

    get diagnostic() { return JSON.stringify(this.editn); }

    SwitchMe(query: string): string {
        if (/power|electricity|wind|solar|nuclear|energy/gi.test(query)) {
            this.img = 'https://www.energymarketprice.com/ivan/uploads/power.png';
            this.title = 'power';
            return 'dpower';

        } else if (/oil|gasoline/gi.test(query)) {
            this.img = 'https://www.energymarketprice.com/ivan/uploads/oil.png';
            this.title = 'oil';
            return 'doil';

        } else if (/coal/gi.test(query)) {
            this.img = 'https://www.energymarketprice.com/ivan/uploads/coal.png';
            this.title = 'coal';
            return 'dcoal';

        } else if (/ gas|gas|LNG/gi.test(query)) {
            this.img = 'https://www.energymarketprice.com/ivan/uploads/naturalgas.png';
            this.title = 'natural gas';
            return 'dgas';

        } else if (/renewables|emissions|Feed in tariffs|Electric Vehicles/gi.test(query)) {
            this.img = 'https://www.energymarketprice.com/ivan/uploads/CO2.png';
            this.title = 'renewables';
            return 'dren';

        } else if (/Daily|daily/gi.test(query)) {
            this.img = 'https://www.energymarketprice.com/ivan/uploads/daily.png';
            this.title = 'daily';
            return 'ddaily';

        } else {
            this.img = 'https://www.energymarketprice.com/ivan/uploads/Economics.png';
            this.title = 'economics';
            return 'deco';
        }

    }
}

