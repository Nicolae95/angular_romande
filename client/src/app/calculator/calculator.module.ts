import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { CalculatorTabComponent } from './calculator-tab/calculator-tab.component';
import { SiteComponent } from './site/site.component';
import { MultisiteComponent } from './multisite/multisite.component';

const routes: Routes = [
  // { path: '**', redirectTo: 're' },
  { path: '', component: CalculatorTabComponent,  data: {title: 'Analytics'},
      children: [
        { path: '', redirectTo: 'site', pathMatch: 'full'},
        { path: 'site', component: SiteComponent, data: {title: 'Site'}},
        { path: 'multisite', component: MultisiteComponent, data: {title: 'Multisite'}},

      ]
    },
  ];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class CalculatorRoutingModule { }
