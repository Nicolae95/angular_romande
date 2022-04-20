import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-news-details',
  templateUrl: './news-details.component.html',
  styleUrls: ['./news-details.component.css']
})




export class NewsDetailsComponent implements OnInit {

@Input() nid: any; // News;

  constructor() { }

  ngOnInit() {
  }

}
