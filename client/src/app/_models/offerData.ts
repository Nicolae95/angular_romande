export class Offer {
    id: number;
    name: string;
    company: number;
    consumption: number;
    pfc: number;
    pfc_market: number;
    profile: number;
    cc: number;
    years: Array<number>;
    lissage_years: Object;
    lissage: boolean;
    unit: string;
    offer_type: string;
    riscs: Array<number>;
    shedules: Array<number>;
    validation_time: number;
    employees: string;
    meters: Array<string>;
    decotes: Object;
    efforts: Object;
    energies: Object;
    majors: Object;
    ps1: Object;
    ps2: Object;

    // constructor(obj: any) {
    //     this.name = obj['nomOffer'];
    //     this.company = obj['company']['id'];
    //     this.consumption = obj['volumeAnnuelTotal'];
    //     this.pfc = obj['pfc'];
    //     this.pfc_market = obj['pfc_market'];
    //     this.profile = obj['profile'];
    //     this.cc = obj['cc'];
    //     this.years = obj['years'];
    //     this.unit = obj['unit'];
    //     this.offer_type = obj['offer_type'];
    //     this.riscs = obj['riscs'];
    //     this.shedules = obj['shedules'];
    //     this.validation_time = obj['validation_time'];
    // }
}
