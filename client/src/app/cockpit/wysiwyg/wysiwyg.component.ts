import { Component, OnInit, ViewEncapsulation  } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import * as $ from 'jquery';
import { DomSanitizer } from '@angular/platform-browser';

interface JQueryStatic {
  FroalaEditor: any;
}

@Component({
  selector: 'app-wysiwyg',
  templateUrl: './wysiwyg.component.html',
  styleUrls: [
    // '../../../assets/css/styles.css',
    // '../../../assets/css/styles/nexus.css',
    // '../../../assets/css/styles/layout.css',
    // '../../../assets/css/styles/animate.css',
    // '../../../assets/css/styles/theme.css'
  ]
})


export class WysiwygComponent implements OnInit {
htmlContent: any;
viewHtml: any;


  ngOnInit() {

  }

  constructor(private sanitizer: DomSanitizer) {}

  ngSubmit(data?: any) {
    console.log('ngSubmit', this.htmlContent);
    this.viewHtml =  this.sanitizer.bypassSecurityTrustHtml(this.htmlContent);
  }

}
