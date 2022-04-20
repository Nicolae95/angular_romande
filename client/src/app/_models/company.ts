export class Company {
    id: number;
    name: string;
    company_id: string;
    surname: string;
    email: string;
    func: string;
    podsRows: string[];
    crm_id: number;
    nom_entrepise: string;
    sex: string;
    files: any;
    zip_code: string;
    address: string;

    constructor(obj: any) {
        this.id = obj.id;
        this.name = obj.name;
        this.company_id = obj.company_id;
        this.surname = obj.surname;
        this.email = obj.email;
        this.func = obj.func;
        this.podsRows = obj.podsRows;
    }
}
