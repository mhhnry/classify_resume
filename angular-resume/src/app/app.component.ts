import { Component } from '@angular/core';
import { DataService } from './data.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'angular-resume';
  fileToUpload: File | null = null;
  responseData: any = null;

  constructor(private dataService: DataService) { }

  handleFileInput(event: any): void {
    this.fileToUpload = event.target.files.item(0);
  }

  uploadFileToActivity(): void {
    if (this.fileToUpload) {
      this.dataService.uploadFile(this.fileToUpload).subscribe((data: any) => {
        console.log(data);
        this.responseData = data;
      }, (error: any) => {
        console.log(error);
      });
    }
  }
}
