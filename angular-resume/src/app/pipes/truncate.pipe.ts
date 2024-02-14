import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'truncate'
})
export class TruncatePipe implements PipeTransform {
  transform(value: string, limit = 25, completeWords = false, ellipsis = '...'): string {
    if (value.length <= limit) {
      return value;
    }
    const finalLimit = completeWords ? value.substr(0, limit).lastIndexOf(' ') : limit;
    return `${value.substr(0, finalLimit)}${ellipsis}`;
  }
}
