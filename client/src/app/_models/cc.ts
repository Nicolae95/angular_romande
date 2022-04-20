export class Cc {
    site: string;
    files: any;
    multisite: boolean;
    company: number;
    years: number[];
    dates: number[];
    meters: string;

    constructor(obj: any) {
        this.site = obj.site;
        this.files = obj.files;
        this.multisite = obj.multisite;
        this.meters = obj.meters;
        this.company = obj.company;
        this.years = obj.years;
        this.dates = obj.dates;
    }
}
