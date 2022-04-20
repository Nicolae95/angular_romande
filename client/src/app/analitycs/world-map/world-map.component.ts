import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-world-map',
  templateUrl: './world-map.component.html',
  styleUrls: ['./world-map.component.css']
})
export class WorldMapComponent implements OnInit {
  @Input() data: any;
  dataSource: Object;
  myData = [
    // { 'id': '118', 'value': 2696 },
    // { 'id': '161', 'value': 2050 },
  ];
  constructor() {


    this.dataSource = {
      // 'showlegend': '1', // show legend
      'chart': {
        'animation': '0',
        'showbevel': '0',
        'usehovercolor': '1',
        'canvasbordercolor': 'FFFFFF',
        'bordercolor': 'FFFFFF',
        'showlegend': '0',
        'showshadow': '0',
        'legendposition': 'BOTTOM',
        'legendborderalpha': '0',
        'legendbordercolor': 'ffffff',
        'legendallowdrag': '0',
        'legendshadow': '0',
        'caption': 'Principaux pays par numéro d\'accès',
        'connectorcolor': '000000',
        'fillalpha': '80',
        'hovercolor': 'CCCCCC',
        'showborder': '0',
        'showLabels': '0'
      },
      'colorrange': {
        'minvalue': '0',
        'startlabel': 'Low',
        'endlabel': 'High',
        'code': 'e44a00',
        'gradient': '1',
        'color': [{ 'maxvalue': '2500', 'code': 'f8bd19' }, { 'maxvalue': '5000', 'code': '6baa01' }]
      },
      'data': this.myData
    };


  }

  ngOnInit() {
    if (this.data) {
      console.log('data', this.data);
      this.data.forEach((element, index ) => {
        switch (element.country) {
          // daca tara vine codul short push id
          case 'AG': this.myData.push({'id': '01', value: element.count}); break; //  01	AG	Antigua and Barbuda
          case 'BS': this.myData.push({'id': '02', value: element.count}); break; //  02	BS	Bahamas
          case 'BB': this.myData.push({'id': '03', value: element.count}); break; //  03	BB	Barbados
          case 'BZ': this.myData.push({'id': '04', value: element.count}); break; //  04	BZ	Belize
          case 'CA': this.myData.push({'id': '05', value: element.count}); break; //  05	CA	Canada
          case 'CR': this.myData.push({'id': '06', value: element.count}); break; //  06	CR	Costa Rica
          case 'CU': this.myData.push({'id': '07', value: element.count}); break; //  07	CU	Cuba
          case 'DM': this.myData.push({'id': '08', value: element.count}); break; //  08	DM	Dominica
          case 'DO': this.myData.push({'id': '09', value: element.count}); break; //  09	DO	Dominican Republic
          case 'SV': this.myData.push({'id': '10', value: element.count}); break; //  10	SV	El Salvador
          case 'GD': this.myData.push({'id': '11', value: element.count}); break; //  11	GD	Grenada
          case 'GT': this.myData.push({'id': '12', value: element.count}); break; //  12	GT	Guatemala
          case 'HT': this.myData.push({'id': '13', value: element.count}); break; //  13	HT	Haiti
          case 'HN': this.myData.push({'id': '14', value: element.count}); break; //  14	HN	Honduras
          case 'JM': this.myData.push({'id': '15', value: element.count}); break; //  15	JM	Jamaica
          case 'MX': this.myData.push({'id': '16', value: element.count}); break; //  16	MX	Mexico
          case 'NI': this.myData.push({'id': '17', value: element.count}); break; //  17	NI	Nicaragua
          case 'PA': this.myData.push({'id': '18', value: element.count}); break; //  18	PA	Panama
          case 'KN': this.myData.push({'id': '19', value: element.count}); break; //  19	KN	St. Kitts & Nevis
          case 'LC': this.myData.push({'id': '20', value: element.count}); break; //  20	LC	St. Lucia
          case 'VC': this.myData.push({'id': '21', value: element.count}); break; //  21	VC	St. Vincent & the Grenadines
          case 'TT': this.myData.push({'id': '22', value: element.count}); break; //  22	TT	Trinidad & Tobago
          case 'US': this.myData.push({'id': '23', value: element.count}); break; //  23	US	United States
          case 'GL': this.myData.push({'id': '24', value: element.count}); break; //  24	GL	Greenland
          case 'AR': this.myData.push({'id': '25', value: element.count}); break; //  25	AR	Argentina
          case 'BO': this.myData.push({'id': '26', value: element.count}); break; //  26	BO	Bolivia
          case 'BR': this.myData.push({'id': '27', value: element.count}); break; //  27	BR	Brazil
          case 'CL': this.myData.push({'id': '28', value: element.count}); break; //  28	CL	Chile
          case 'CO': this.myData.push({'id': '29', value: element.count}); break; //  29	CO	Colombia
          case 'EC': this.myData.push({'id': '30', value: element.count}); break; //  30	EC	Ecuador
          case 'FK': this.myData.push({'id': '31', value: element.count}); break; //  31	FK	Falkland Islands
          case 'GF': this.myData.push({'id': '32', value: element.count}); break; //  32	GF	French Guiana
          case 'GY': this.myData.push({'id': '33', value: element.count}); break; //  33	GY	Guyana
          case 'PY': this.myData.push({'id': '34', value: element.count}); break; //  34	PY	Paraguay
          case 'PE': this.myData.push({'id': '35', value: element.count}); break; //  35	PE	Peru
          case 'SR': this.myData.push({'id': '36', value: element.count}); break; //  36	SR	Suriname
          case 'UY': this.myData.push({'id': '37', value: element.count}); break; //  37	UY	Uruguay
          case 'VE': this.myData.push({'id': '38', value: element.count}); break; //  38	VE	Venezuela
          case 'DZ': this.myData.push({'id': '39', value: element.count}); break; //  39	DZ	Algeria
          case 'AO': this.myData.push({'id': '40', value: element.count}); break; //  40	AO	Angola
          case 'BJ': this.myData.push({'id': '41', value: element.count}); break; //  41	BJ	Benin
          case 'BW': this.myData.push({'id': '42', value: element.count}); break; //  42	BW	Botswana
          case 'BF': this.myData.push({'id': '43', value: element.count}); break; //  43	BF	Burkina Faso
          case 'BI': this.myData.push({'id': '44', value: element.count}); break; //  44	BI	Burundi
          case 'CM': this.myData.push({'id': '45', value: element.count}); break; //  45	CM	Cameon
          case 'CV': this.myData.push({'id': '46', value: element.count}); break; //  46	CV	Cape Verde
          case 'CP': this.myData.push({'id': '47', value: element.count}); break; //  47	CP	Central African Republic
          case 'TD': this.myData.push({'id': '48', value: element.count}); break; //  48	TD	Chad
          case 'KM': this.myData.push({'id': '49', value: element.count}); break; //  49	KM	Comoros
          case 'CI': this.myData.push({'id': '50', value: element.count}); break; //  50	CI	Ivory Coast
          case 'CD': this.myData.push({'id': '51', value: element.count}); break; //  51	CD	DR Congo
          case 'DJ': this.myData.push({'id': '52', value: element.count}); break; //  52	DJ	Djibouti
          case 'EG': this.myData.push({'id': '53', value: element.count}); break; //  53	EG	Egypt
          case 'GQ': this.myData.push({'id': '54', value: element.count}); break; //  54	GQ	Equatorial Guinea
          case 'ER': this.myData.push({'id': '55', value: element.count}); break; //  55	ER	Eritrea
          case 'ET': this.myData.push({'id': '56', value: element.count}); break; //  56	ET	Ethiopia
          case 'GA': this.myData.push({'id': '57', value: element.count}); break; //  57	GA	Gabon
          case 'GH': this.myData.push({'id': '58', value: element.count}); break; //  58	GH	Ghana
          case 'GN': this.myData.push({'id': '59', value: element.count}); break; //  59	GN	Guinea
          case 'GW': this.myData.push({'id': '60', value: element.count}); break; //  60	GW	Guinea-Bissau
          case 'KE': this.myData.push({'id': '61', value: element.count}); break; //  61	KE	Kenya
          case 'LS': this.myData.push({'id': '62', value: element.count}); break; //  62	LS	Lesotho
          case 'LI': this.myData.push({'id': '63', value: element.count}); break; //  63	LI	Liberia
          case 'LR': this.myData.push({'id': '64', value: element.count}); break; //  64	LR	Libya
          case 'MS': this.myData.push({'id': '65', value: element.count}); break; //  65	MS	Madagascar
          case 'MW': this.myData.push({'id': '66', value: element.count}); break; //  66	MW	Malawi
          case 'ML': this.myData.push({'id': '67', value: element.count}); break; //  67	ML	Mali
          case 'MR': this.myData.push({'id': '68', value: element.count}); break; //  68	MR	Mauritania
          case 'MA': this.myData.push({'id': '69', value: element.count}); break; //  69	MA	Morocco
          case 'MZ': this.myData.push({'id': '70', value: element.count}); break; //  70	MZ	Mozambique
          case 'NA': this.myData.push({'id': '71', value: element.count}); break; //  71	NA	Namibia
          case 'NE': this.myData.push({'id': '72', value: element.count}); break; //  72	NE	Niger
          case 'NG': this.myData.push({'id': '73', value: element.count}); break; //  73	NG	Nigeria
          case 'RW': this.myData.push({'id': '74', value: element.count}); break; //  74	RW	Rwanda
          case 'ST': this.myData.push({'id': '75', value: element.count}); break; //  75	ST	Sao Tome and Principe
          case 'SN': this.myData.push({'id': '76', value: element.count}); break; //  76	SN	Senegal
          case 'SC': this.myData.push({'id': '77', value: element.count}); break; //  77	SC	Seychelles
          case 'SL': this.myData.push({'id': '78', value: element.count}); break; //  78	SL	Sierra Leone
          case 'SO': this.myData.push({'id': '79', value: element.count}); break; //  79	SO	Somalia
          case 'ZA': this.myData.push({'id': '80', value: element.count}); break; //  80	ZA	South Africa
          case 'SD': this.myData.push({'id': '81', value: element.count}); break; //  81	SD	Republic of Sudan
          case 'SZ': this.myData.push({'id': '82', value: element.count}); break; //  82	SZ	Swaziland
          case 'TZ': this.myData.push({'id': '83', value: element.count}); break; //  83	TZ	Tanzania
          case 'TG': this.myData.push({'id': '84', value: element.count}); break; //  84	TG	Togo
          case 'TN': this.myData.push({'id': '85', value: element.count}); break; //  85	TN	Tunisia
          case 'UG': this.myData.push({'id': '86', value: element.count}); break; //  86	UG	Uganda
          case 'WA': this.myData.push({'id': '87', value: element.count}); break; //  87	WA	Western Sahara
          case 'ZM': this.myData.push({'id': '88', value: element.count}); break; //  88	ZM	Zambia
          case 'ZW': this.myData.push({'id': '89', value: element.count}); break; //  89	ZW	Zimbabwe
          case 'GM': this.myData.push({'id': '90', value: element.count}); break; //  90	GM	Gambia
          case 'CG': this.myData.push({'id': '91', value: element.count}); break; //  91	CG	Congo
          case 'MI': this.myData.push({'id': '92', value: element.count}); break; //  92	MI	Mauritius
          case 'AF': this.myData.push({'id': '93', value: element.count}); break; //  93	AF	Afghanistan
          case 'AM': this.myData.push({'id': '94', value: element.count}); break; //  94	AM	Armenia
          case 'AZ': this.myData.push({'id': '95', value: element.count}); break; //  95	AZ	Azerbaijan
          case 'BD': this.myData.push({'id': '96', value: element.count}); break; //  96	BD	Bangladesh
          case 'BT': this.myData.push({'id': '97', value: element.count}); break; //  97	BT	Bhutan
          case 'BN': this.myData.push({'id': '98', value: element.count}); break; //  98	BN	Brunei
          case 'MM': this.myData.push({'id': '99', value: element.count}); break; //  99	MM	Burma (Myanmar)
          case 'KH': this.myData.push({'id': '100', value: element.count}); break; //  100	KH	Cambodia
          case 'CN': this.myData.push({'id': '101', value: element.count}); break; //  101	CN	China
          case 'TP': this.myData.push({'id': '102', value: element.count}); break; //  102	TP	Timor-Leste
          case 'GE': this.myData.push({'id': '103', value: element.count}); break; //  103	GE	Georgia
          case 'IN': this.myData.push({'id': '104', value: element.count}); break; //  104	IN	India
          case 'ID': this.myData.push({'id': '105', value: element.count}); break; //  105	ID	Indonesia
          case 'IA': this.myData.push({'id': '106', value: element.count}); break; //  106	IA	Iran
          case 'JP': this.myData.push({'id': '107', value: element.count}); break; //  107	JP	Japan
          case 'KZ': this.myData.push({'id': '108', value: element.count}); break; //  108	KZ	Kazakhstan
          case 'KP': this.myData.push({'id': '109', value: element.count}); break; //  109	KP	Korea (north)
          case 'KR': this.myData.push({'id': '110', value: element.count}); break; //  110	KR	Korea (south)
          case 'KG': this.myData.push({'id': '111', value: element.count}); break; //  111	KG	Kyrgyzstan
          case 'LA': this.myData.push({'id': '112', value: element.count}); break; //  112	LA	Laos
          case 'MY': this.myData.push({'id': '113', value: element.count}); break; //  113	MY	Malaysia
          case 'MN': this.myData.push({'id': '114', value: element.count}); break; //  114	MN	Mongolia
          case 'NP': this.myData.push({'id': '115', value: element.count}); break; //  115	NP	Nepal
          case 'PK': this.myData.push({'id': '116', value: element.count}); break; //  116	PK	Pakistan
          case 'PH': this.myData.push({'id': '117', value: element.count}); break; //  117	PH	Philippines
          case 'RU': this.myData.push({'id': '118', value: element.count}); break; //  118	RU	Russia
          case 'SG': this.myData.push({'id': '119', value: element.count}); break; //  119	SG	Singapore
          case 'LK': this.myData.push({'id': '120', value: element.count}); break; //  120	LK	Sri Lanka
          case 'TJ': this.myData.push({'id': '121', value: element.count}); break; //  121	TJ	Tajikistan
          case 'TH': this.myData.push({'id': '122', value: element.count}); break; //  122	TH	Thailand
          case 'TM': this.myData.push({'id': '123', value: element.count}); break; //  123	TM	Turkmenistan
          case 'UZ': this.myData.push({'id': '124', value: element.count}); break; //  124	UZ	Uzbekistan
          case 'VN': this.myData.push({'id': '125', value: element.count}); break; //  125	VN	Vietnam
          case 'TW': this.myData.push({'id': '126', value: element.count}); break; //  126	TW	Taiwan
          case 'HK': this.myData.push({'id': '127', value: element.count}); break; //  127	HK	Hong Kong
          case 'MO': this.myData.push({'id': '128', value: element.count}); break; //  128	MO	Macau
          case 'AL': this.myData.push({'id': '129', value: element.count}); break; //  129	AL	Albania
          case 'AD': this.myData.push({'id': '130', value: element.count}); break; //  130	AD	Andorra
          case 'AT': this.myData.push({'id': '131', value: element.count}); break; //  131	AT	Austria
          case 'BY': this.myData.push({'id': '132', value: element.count}); break; //  132	BY	Belarus
          case 'BE': this.myData.push({'id': '133', value: element.count}); break; //  133	BE	Belgium
          case 'BH': this.myData.push({'id': '134', value: element.count}); break; //  134	BH	Bosnia and Herzegovina
          case 'BG': this.myData.push({'id': '135', value: element.count}); break; //  135	BG	Bulgaria
          case 'HY': this.myData.push({'id': '136', value: element.count}); break; //  136	HY	Croatia
          case 'CZ': this.myData.push({'id': '137', value: element.count}); break; //  137	CZ	Czech Republic
          case 'DK': this.myData.push({'id': '138', value: element.count}); break; //  138	DK	Denmark
          case 'EE': this.myData.push({'id': '139', value: element.count}); break; //  139	EE	Estonia
          case 'FI': this.myData.push({'id': '140', value: element.count}); break; //  140	FI	Finland
          case 'FR': this.myData.push({'id': '141', value: element.count}); break; //  141	FR	France
          case 'DE': this.myData.push({'id': '142', value: element.count}); break; //  142	DE	Germany
          case 'GR': this.myData.push({'id': '143', value: element.count}); break; //  143	GR	Greece
          case 'HU': this.myData.push({'id': '144', value: element.count}); break; //  144	HU	Hungary
          case 'IC': this.myData.push({'id': '145', value: element.count}); break; //  145	IC	Iceland
          case 'IR': this.myData.push({'id': '146', value: element.count}); break; //  146	IR	Ireland
          case 'IT': this.myData.push({'id': '147', value: element.count}); break; //  147	IT	Italy
          case 'LV': this.myData.push({'id': '148', value: element.count}); break; //  148	LV	Latvia
          case 'LN': this.myData.push({'id': '149', value: element.count}); break; //  149	LN	Liechtenstein
          case 'LT': this.myData.push({'id': '150', value: element.count}); break; //  150	LT	Lithuania
          case 'LU': this.myData.push({'id': '151', value: element.count}); break; //  151	LU	Luxembourg
          case 'MK': this.myData.push({'id': '152', value: element.count}); break; //  152	MK	Macedonia
          case 'MT': this.myData.push({'id': '153', value: element.count}); break; //  153	MT	Malta
          case 'MV': this.myData.push({'id': '154', value: element.count}); break; //  154	MV	Moldova
          case 'MC': this.myData.push({'id': '155', value: element.count}); break; //  155	MC	Monaco
          case 'MG': this.myData.push({'id': '156', value: element.count}); break; //  156	MG	Montenegro
          case 'NL': this.myData.push({'id': '157', value: element.count}); break; //  157	NL	Netherlands
          case 'NO': this.myData.push({'id': '158', value: element.count}); break; //  158	NO	Norway
          case 'PL': this.myData.push({'id': '159', value: element.count}); break; //  159	PL	Poland
          case 'PT': this.myData.push({'id': '160', value: element.count}); break; //  160	PT	Portugal
          case 'RO': this.myData.push({'id': '161', value: element.count}); break; //  161	RO	Romania
          case 'SM': this.myData.push({'id': '162', value: element.count}); break; //  162	SM	San Marino
          case 'CS': this.myData.push({'id': '163', value: element.count}); break; //  163	CS	Serbia
          case 'SK': this.myData.push({'id': '164', value: element.count}); break; //  164	SK	Slovakia
          case 'SI': this.myData.push({'id': '165', value: element.count}); break; //  165	SI	Slovenia
          case 'ES': this.myData.push({'id': '166', value: element.count}); break; //  166	ES	Spain
          case 'SE': this.myData.push({'id': '167', value: element.count}); break; //  167	SE	Sweden
          case 'CH': this.myData.push({'id': '168', value: element.count}); break; //  168	CH	Switzerland
          case 'UA': this.myData.push({'id': '169', value: element.count}); break; //  169	UA	Ukraine
          case 'UK': this.myData.push({'id': '170', value: element.count}); break; //  170	UK	United Kingdom
          case 'VA': this.myData.push({'id': '171', value: element.count}); break; //  171	VA	Vatican City
          case 'CY': this.myData.push({'id': '172', value: element.count}); break; //  172	CY	Cyprus
          case 'TK': this.myData.push({'id': '173', value: element.count}); break; //  173	TK	Turkey
          case 'AU': this.myData.push({'id': '175', value: element.count}); break; //  175	AU	Australia
          case 'FJ': this.myData.push({'id': '176', value: element.count}); break; //  176	FJ	Fiji
          case 'KI': this.myData.push({'id': '177', value: element.count}); break; //  177	KI	Kiribati
          case 'MH': this.myData.push({'id': '178', value: element.count}); break; //  178	MH	Marshall Islands
          case 'FM': this.myData.push({'id': '179', value: element.count}); break; //  179	FM	Micronesia
          case 'NR': this.myData.push({'id': '180', value: element.count}); break; //  180	NR	Nauru
          case 'NZ': this.myData.push({'id': '181', value: element.count}); break; //  181	NZ	New Zealand
          case 'PW': this.myData.push({'id': '182', value: element.count}); break; //  182	PW	Republic of Palau
          case 'PG': this.myData.push({'id': '183', value: element.count}); break; //  183	PG	Papua New Guinea
          case 'WS': this.myData.push({'id': '184', value: element.count}); break; //  184	WS	Samoa
          case 'SB': this.myData.push({'id': '185', value: element.count}); break; //  185	SB	Solomon Islands
          case 'TO': this.myData.push({'id': '186', value: element.count}); break; //  186	TO	Tonga
          case 'TV': this.myData.push({'id': '187', value: element.count}); break; //  187	TV	Tuvalu
          case 'VU': this.myData.push({'id': '188', value: element.count}); break; //  188	VU	Vanuatu
          case 'NC': this.myData.push({'id': '189', value: element.count}); break; //  189	NC	New Caledonia
          case 'BA': this.myData.push({'id': '190', value: element.count}); break; //  190	BA	Bahrain
          case 'IZ': this.myData.push({'id': '191', value: element.count}); break; //  191	IZ	Iraq
          case 'IS': this.myData.push({'id': '192', value: element.count}); break; //  192	IS	Israel
          case 'JO': this.myData.push({'id': '193', value: element.count}); break; //  193	JO	Jordan
          case 'KU': this.myData.push({'id': '194', value: element.count}); break; //  194	KU	Kuwait
          case 'LB': this.myData.push({'id': '195', value: element.count}); break; //  195	LB	Lebanon
          case 'OM': this.myData.push({'id': '196', value: element.count}); break; //  196	OM	Oman
          case 'QA': this.myData.push({'id': '197', value: element.count}); break; //  197	QA	Qatar
          case 'SA': this.myData.push({'id': '198', value: element.count}); break; //  198	SA	Saudi Arabia
          case 'SY': this.myData.push({'id': '199', value: element.count}); break; //  199	SY	Syria
          case 'AE': this.myData.push({'id': '200', value: element.count}); break; //  200	AE	UnitedArabEmirates
          case 'YM': this.myData.push({'id': '201', value: element.count}); break; //  201	YM	Yemen
          case 'PR': this.myData.push({'id': '202', value: element.count}); break; //  202	PR	Puerto Rico
          case 'KY': this.myData.push({'id': '203', value: element.count}); break; //  203	KY	Cayman Islands
          case 'SS': this.myData.push({'id': '204', value: element.count}); break; //  204	SS	South Sudan
          case 'KO': this.myData.push({'id': '205', value: element.count}); break; //  205	KO	Kosovo
          case 'AB': this.myData.push({'id': '206', value: element.count}); break; //  206	AB	Aruba
          case 'AN': this.myData.push({'id': '207', value: element.count}); break; //  207	AN	Anguilla
          case 'AS': this.myData.push({'id': '208', value: element.count}); break; //  208	AS	American Samoa
          case 'BM': this.myData.push({'id': '209', value: element.count}); break; //  209	BM	Bermuda
          case 'BU': this.myData.push({'id': '210', value: element.count}); break; //  210	BU	BES Islands
          case 'CC': this.myData.push({'id': '211', value: element.count}); break; //  211	CC	Cocos (Keeling) Islands
          case 'CK': this.myData.push({'id': '212', value: element.count}); break; //  212	CK	Cook Islands
          case 'CT': this.myData.push({'id': '213', value: element.count}); break; //  213	CT	Christmas Island
          case 'CW': this.myData.push({'id': '214', value: element.count}); break; //  214	CW	Curacao
          case 'FA': this.myData.push({'id': '215', value: element.count}); break; //  215	FA	Faroe Islands
          case 'FP': this.myData.push({'id': '216', value: element.count}); break; //  216	FP	French Polynesia
          case 'GI': this.myData.push({'id': '217', value: element.count}); break; //  217	GI	Gibraltar
          case 'GO': this.myData.push({'id': '218', value: element.count}); break; //  218	GO	Guam
          case 'GP': this.myData.push({'id': '219', value: element.count}); break; //  219	GP	Guadeloupe
          case 'GS': this.myData.push({'id': '220', value: element.count}); break; //  220	GS	Gaza Strip
          case 'GU': this.myData.push({'id': '221', value: element.count}); break; //  221	GU	Guernsey
          case 'IM': this.myData.push({'id': '222', value: element.count}); break; //  222	IM	Isle of Man
          case 'JS': this.myData.push({'id': '223', value: element.count}); break; //  223	JS	Jersey
          case 'KS': this.myData.push({'id': '224', value: element.count}); break; //  224	KS	Kingman Reef
          case 'MD': this.myData.push({'id': '225', value: element.count}); break; //  225	MD	Maldives
          case 'ME': this.myData.push({'id': '226', value: element.count}); break; //  226	ME	Montserrat
          case 'MP': this.myData.push({'id': '227', value: element.count}); break; //  227	MP	Mayotte
          case 'MQ': this.myData.push({'id': '228', value: element.count}); break; //  228	MQ	Martinique
          case 'NF': this.myData.push({'id': '229', value: element.count}); break; //  229	NF	Norfolk Island
          case 'NM': this.myData.push({'id': '230', value: element.count}); break; //  230	NM	Northern Mariana Islands
          case 'NU': this.myData.push({'id': '231', value: element.count}); break; //  231	NU	Niue
          case 'PI': this.myData.push({'id': '232', value: element.count}); break; //  232	PI	Pitcairn Islands
          case 'RE': this.myData.push({'id': '233', value: element.count}); break; //  233	RE	La Réunion
          case 'SF': this.myData.push({'id': '234', value: element.count}); break; //  234	SF	Sint Maarten
          case 'SH': this.myData.push({'id': '235', value: element.count}); break; //  235	SH	Saint Helena
          case 'SP': this.myData.push({'id': '236', value: element.count}); break; //  236	SP	Saint Pierre and Miquelon
          case 'TC': this.myData.push({'id': '237', value: element.count}); break; //  237	TC	Turks and Caicos Islands
          case 'VK': this.myData.push({'id': '238', value: element.count}); break; //  238	VK	Virgin Islands (UK)
          case 'VS': this.myData.push({'id': '239', value: element.count}); break; //  239	VS	Virgin Islands (US)
          case 'WE': this.myData.push({'id': '240', value: element.count}); break; //  240	WE	Palestine
          case 'WF': this.myData.push({'id': '241', value: element.count}); break; //  241	WF	Wallis and Futuna
          case 'WC': this.myData.push({'id': '242', value: element.count}); break; //  242	WC	Cape Town
          case 'LP': this.myData.push({'id': '243', value: element.count}); break; //  243	LP	La Paz
          case 'AB': this.myData.push({'id': '244', value: element.count}); break; //  244	AB	Abkhazia
          case 'NA': this.myData.push({'id': '245', value: element.count}); break; //  245	NA	Netherlands Antilles
          case 'NC': this.myData.push({'id': '246', value: element.count}); break; //  246	NC	Northern Cyprus
          case 'SV': this.myData.push({'id': '247', value: element.count}); break; //  247	SV	Svalbard
          case 'TK': this.myData.push({'id': '248', value: element.count}); break; //  248	TK	Tokelau
        }

      });
      // console.log('mydata', this.myData);

    }

    }

}

