  export class News {
    id: number;
    created: string;
    title: string;
    source: string;
    validated_text: string;
  }

  // export class ChartSeries {
  //     name: string;
  //   //   data: ChartData[] = [];
  //     data: any;
  //     yAxis: number;
  // }



export class NewsForm {
    constructor(
        public ckid: number,
        public name: string,
        public numberof: number,
        public categories: boolean[]
    ) {}
}
