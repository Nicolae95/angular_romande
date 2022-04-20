import { CcComponent } from './components/cc/cc.component';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './components/home/index';
import { RegisterComponent } from './components/register/index';
import { AuthGuard } from './_guards/index';
import { CompanyComponent } from './components/company/company.component';
import { CcUploadComponent } from './components/ccupload/ccupload.component';
import { OfferComponent } from './components/offer/offer.component';
import { OffermailComponent } from './components/offermail/offermail.component';
import { AdmincontrolsComponent } from './components/admincontrols/admincontrols.component';
import { TranslateComponent } from './components/translate/translate.component';
import { TableofferComponent } from './components/tableoffer/tableoffer.component';
import { PaginationOfferComponent } from './components/paginationOffer/paginationOffer.component';
import { OffercockpitComponent } from './components/offercockpit/offercockpit.component';
import { SiteDashboardComponent } from './components/site-dashboard/site-dashboard.component';
import { PondereComponent } from './components/pondere/pondere.component';
import { PrimesDeRisqueComponent } from './components/primes-de-risque/primes-de-risque.component';
import { DataHubComponent } from './components/data-hub/data-hub.component';
import { EcoEnergiesComponent } from './components/eco-energies/eco-energies.component';
import { ClientsComponent } from './components/clients/clients.component';
import { SetPasswordComponent } from './components/set-password/set-password.component';
import { MyDezactives } from './_guards/dezactive.guard';
import { RisqueComponent } from './components/risque/risque.component';
// import { AddCockpitComponent } from './components/add-cockpit/add-cockpit.component';
import { EditCockpitBComponent } from './components/edit-cockpit-b/edit-cockpit-b.component';
import { LoginComponent } from './components/login/login.component';
import { HeaderComponent } from './components/header/header.component';
import { InfOfferComponent } from './components/inf-offer/inf-offer.component';
import { CockpitModule } from './cockpit/cockpit.module';



const appRoutes: Routes = [
    { path: 'login',            component: LoginComponent,           data: {title: 'Login'            }},
    { path: 'mail/:token',      component: OffermailComponent,       data: {title: 'Offer Mail'       }},
    { path: 'password/:token',  component: SetPasswordComponent,     data: {title: 'Mot de passe'     }},
    { path: 'cockpits',         loadChildren: './cockpit/cockpit.module#CockpitModule' },


    { path: '', component: HeaderComponent, canActivate: [AuthGuard],
        children: [
            { path: '',   redirectTo: 'clients', pathMatch: 'full'},
            { path: 'pfc',              loadChildren: './pfc/pfc.module#PfcModule'                            },
            { path: 'analytics',        loadChildren: './analitycs/analitycs.module#AnalitycsModule'          },
            { path: 'calculator', loadChildren: './calculator/calculatorR.module#CalculatorModule' },
            { path: 'clients',          component: ClientsComponent,         data: {title: 'Clients'          }},
            { path: 'admins',           component: AdmincontrolsComponent,   data: {title: 'Admins'           }},
            { path: 'cockpit',          component: OffercockpitComponent,    data: {title: 'Offers Cockpit'   }},
            { path: 'offers',           component: PaginationOfferComponent, data: {title: 'Offers'           }},
            { path: 'risque',           component: PrimesDeRisqueComponent,  data: {title: 'Primes De Risque' }},
            { path: 'ecoenergies',      component: EcoEnergiesComponent,     data: {title: 'Eco-Energies'     }},
            { path: 'datahub',          component: DataHubComponent,         data: {title: 'Data hub'         }},
            { path: 'pondere',          component: PondereComponent,         data: {title: 'Profils CC Types' }},
            { path: 'offer/:id/:lc/:c', component: InfOfferComponent,        data: {title: 'Information Offre'}},

            { path: 'account',          component: CcComponent,               data: {title: 'Client '          },
                children: [
                    { path: '', redirectTo: 'offers', pathMatch: 'full'},
                    { path: 'offers/:id', component: TableofferComponent, data: {title: 'Offer'},
                    children: [
                        { path: 'nouveau', redirectTo: '', pathMatch: 'full'},
                        { path: '', component: OfferComponent,  data: {title: 'Nouveau'}}]
                    },
                    { path: 'upload/:id', component: CcUploadComponent, data: {title: 'Upload'},
                        children: [
                        { path: 'translate', component: TranslateComponent, data: {title: 'Translate'}},
                        { path: 'dashboard', component: SiteDashboardComponent, data: {title: 'Dashboard'}},
                    ]},
                ],
            },

            { path: '**', redirectTo: 'clients' },



        ],
    },
    // { path: 'accounts', component: HomeComponent, canActivate: [AuthGuard], data: {title: 'Account'},
    //     children: [
    //         { path: 'clients', component: ClientsComponent, canActivate: [AuthGuard], data: {title: 'Clients'} },
    //         { path: 'admins', component: AdmincontrolsComponent, canActivate: [AuthGuard], data: {title: 'Admins'}
    //     },
    //         { path: '', redirectTo: 'clients', pathMatch: 'full'}
    //     ],
    // },

    // { path: 'account', component: CcComponent, canActivate: [AuthGuard], data: {title: 'Client '},
    //     children: [
    //         { path: '', redirectTo: 'offers', pathMatch: 'full'},
    //         { path: 'offers/:id', component: TableofferComponent, data: {title: 'Offer'},
    //         children: [
    //             { path: 'nouveau', redirectTo: '', pathMatch: 'full'},
    //             { path: '', component: OfferComponent,  data: {title: 'Nouveau'}}]
    //         },
    //         { path: 'upload/:id', component: CcUploadComponent, data: {title: 'Upload'},
    //             children: [
    //             { path: 'translate', component: TranslateComponent, data: {title: 'Translate'}},
    //             { path: 'dashboard', component: SiteDashboardComponent, data: {title: 'Dashboard'}},
    //         ]},
    //     ],
    // },

    // // { path: 'dashboard', component: SiteDashboardComponent, canActivate: [AuthGuard], data: {title: 'Dashboard'}},
    // { path: 'company/:id', component: CompanyComponent, canActivate: [AuthGuard], data: {title: 'Company'}},
    // { path: 'register', component: RegisterComponent, data: {title: 'Register'}},
    // { path: 'offer/mail/:token', component: OffermailComponent, canDeactivate: [MyDezactives], data: {title: 'Offer Mail'}},
    // //  { path: 'risque', component: RisqueComponent, canActivate: [AuthGuard] , data: {title: 'Risque'}},
    // { path: 'risque', component: PrimesDeRisqueComponent, canActivate: [AuthGuard] , data: {title: 'Primes De Risque '}},
    // { path: 'pondere', component: PondereComponent, canActivate: [AuthGuard] , data: {title: 'Profils CC Types'}},
    // { path: 'cockpit/edit/:id', component: EditCockpitBComponent, canActivate: [AuthGuard] , data: {title: 'Edit Cockpit'}},
    // { path: 'offers', component: PaginationOfferComponent, canActivate: [AuthGuard] , data: {title: 'Offers'}},
    // { path: 'market', component: PfcMarketComponent, canActivate: [AuthGuard], data: {title: 'Market'},
    //     children: [
    //         { path: '', redirectTo: 'upload', pathMatch: 'full'},
    //         { path: 'upload', component: PfcMarketUploadComponent, canActivate: [AuthGuard], data: {title: 'Upload'}}
    //     ]
    // },
    // { path: 'pfc', component: PfcComponent, canActivate: [AuthGuard] , data: {title: 'Pfc'},
    //     children: [
    //         { path: '', redirectTo: 'upload', pathMatch: 'full'},
    //         { path: 'upload', component: PfcUploadComponent, canActivate: [AuthGuard], data: {title: 'Upload'}}]
    // },
    // { path: 'datahub', component: DataHubComponent, canActivate: [AuthGuard] , data: {title: 'Data hub'}},

    // { path: 'ecoenergies', component: EcoEnergiesComponent, canActivate: [AuthGuard] , data: {title: ' Eco-Energies'}},
    // // { path: 'analytics', component: AnalyticsComponent, canActivate: [AuthGuard] , data: {title: 'Analytics'},
    // //     children: [
    // //         { path: '', redirectTo: 'tableau', pathMatch: 'full'},
    // //         { path: 'tableau', component: AnlTablauBordComponent, data: {title: 'Tableau de bord'}},
    // //         { path: 'offres', component: AnlOffersComponent, data: {title: 'Offres'}},
    // //         { path: 'activite', component: AnlActivitiClientComponent, data: {title: 'Activité'}}]
    // // },
    // // { path: 'work', component: WysiwygComponent, data: {title: 'Work Hard Play Hard'}},
    // // {
    // //     path: 'analytics',
    // //     loadChildren: './analitycs/analitycs.module#AnalitycsModule'
    // //   },
    // { path: 'password/:token', component: SetPasswordComponent, data: {title: 'Mot de passe'}},
    { path: '**', redirectTo: 'header' },


];

export const routing = RouterModule.forRoot(appRoutes);
//    export const routing = appRoutes;
