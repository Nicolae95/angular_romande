import { Client } from './client';
import { Admin } from './admin';

export class ClientLog {
    client: Client;
    admin: Admin;
    id: number;
    created: string;
    log_type: string;
    offer_name: string;
}
