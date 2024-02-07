import { Component } from '@angular/core';
import { DataService } from './data.service';
import { ChangeDetectorRef } from '@angular/core';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'angular-resume';
  filesToUpload: File[] | null = null;
  responseData: any = null;
  processing: boolean = false;
  tableData: any[] = []; // Add this line

  constructor(private dataService: DataService, private cd: ChangeDetectorRef) { }

  handleFileInput(event: any): void {
    this.filesToUpload = event.target.files;
  }

  uploadFileToActivity(): void {
    if (this.filesToUpload) {
      const formData: FormData = new FormData();
      for (let i = 0; i < this.filesToUpload.length; i++) {
        formData.append('files[]', this.filesToUpload[i], this.filesToUpload[i].name);
      }
      
      this.processing = true;
      this.dataService.uploadFiles(formData).subscribe((data: any) => {
        console.log(data);
        this.responseData = data;
        this.processing = false;
        this.getDataFromServer(); // Call method to retrieve data after processing
      }, (error: any) => {
        console.log(error);
        this.processing = false;
      });
    }
  }

  getDataFromServer(): void {
    this.dataService.getData().subscribe((data: any) => {
      console.log('Data received from server:', data); // Log to check server response
      this.responseData = data;
      this.parseCSVData(data.data); // Parse CSV data
    }, (error: any) => {
      console.error('Error fetching data from server:', error);
    });
  }
  


  // Method to parse CSV data
  parseCSVData(csvData: string): void {
    const lines = csvData.split('\n');
    const result = [];
    const headers = lines[0].split(',');

    for (let i = 1; i < lines.length - 1; i++) { // Adjusted to skip the last empty line if present
      const obj: { [key: string]: string } = {};
      const currentline = lines[i].split(',');
      for (let j = 0; j < headers.length; j++) {
        obj[headers[j]] = currentline[j];
      }
      result.push(obj);
    }

    this.tableData = result; // Assign parsed data for display
    this.cd.detectChanges(); // Manually trigger change detection
    console.log('Parsed table data:', this.tableData); // Log to check parsed data
  }


}
