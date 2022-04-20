import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable(
  // {providedIn: 'root'}
  )

export class SharableService {

    private activedef = new BehaviorSubject(false);
    private actdel = new BehaviorSubject(false);
    private bgcolor = new BehaviorSubject('#ffffff');
    private fontcolor = new BehaviorSubject('#37475a');

    private bgcolor1 = new BehaviorSubject('#ffffff');
    private fontcolor1 = new BehaviorSubject('#37475a');

    private bgcolor2 = new BehaviorSubject('#ffffff');
    private fontcolor2 = new BehaviorSubject('#37475a');

    private bgcolor3 = new BehaviorSubject('#ffffff');
    private fontcolor3 = new BehaviorSubject('#37475a');

    private bgcolor4 = new BehaviorSubject('#ffffff');
    private fontcolor4 = new BehaviorSubject('#37475a');

    private auxcolorbg = new BehaviorSubject('#ffffff');
    private auxcolorf = new BehaviorSubject('#37475a');

    private colorOrder = new BehaviorSubject(0);

    colorBg = this.bgcolor.asObservable();
    colorFont = this.fontcolor.asObservable();

    colorBg1 = this.bgcolor1.asObservable();
    colorFont1 = this.fontcolor1.asObservable();

    colorBg2 = this.bgcolor2.asObservable();
    colorFont2 = this.fontcolor2.asObservable();

    colorBg3 = this.bgcolor3.asObservable();
    colorFont3 = this.fontcolor3.asObservable();

    colorBg4 = this.bgcolor4.asObservable();
    colorFont4 = this.fontcolor4.asObservable();

    colorbg = this.auxcolorbg.asObservable();
    colorf = this.auxcolorf.asObservable();

    active = this.activedef.asObservable();
    adel =  this.actdel.asObservable();

    co = this.colorOrder.asObservable();


  constructor() { }

  changeAuxColorBg(aux: string) {
    this.auxcolorbg.next(aux);
  }

  changeAuxColorF(aux: string) {
    this.auxcolorf.next(aux);
  }

  changeActive(aux: boolean) {
        this.activedef.next(aux);
    }

  changeCO(aux: number) {
    this.colorOrder.next(aux);
  }

    changeColorBG(bgc: string) {
        this.bgcolor.next(bgc);
    }

  changeColorBG1(bgc: string) {
      this.bgcolor1.next(bgc);
    }

  changeColorBG2(bgc: string) {
      this.bgcolor2.next(bgc);
    }

  changeColorBG3(bgc: string) {
      this.bgcolor3.next(bgc);
    }

  changeColorBG4(bgc: string) {
      this.bgcolor4.next(bgc);
    }

  changeColorF(fc: string) {
      this.fontcolor.next(fc);
    }

  changeColorF1(fc: string) {
      this.fontcolor1.next(fc);
    }

  changeColorF2(fc: string) {
      this.fontcolor2.next(fc);
    }

  changeColorF3(fc: string) {
      this.fontcolor3.next(fc);
    }

  changeColorF4(fc: string) {
      this.fontcolor4.next(fc);
    }

    changeDel(aux: boolean) {
        this.actdel.next(aux);
    }

}
