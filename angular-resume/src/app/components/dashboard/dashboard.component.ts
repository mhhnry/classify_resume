import { Component, ChangeDetectorRef, OnInit } from '@angular/core';
import { DataService } from '../../data.service';
import { parse } from 'papaparse';

interface DataRow {
  [key: string]: string | string[];
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  title = 'angular-resume';
  filesToUpload: File[] | null = null;
  responseData: any = null;
  processing: boolean = false;
  tableData: DataRow[] = [];
  displayedColumns: string[] = [];

  constructor(private dataService: DataService, private cd: ChangeDetectorRef) { }

  ngOnInit(): void {
    // Intentionally blank for initialization
  }

  handleFileInput(event: any): void {
    this.filesToUpload = event.target.files;
  }

  uploadFileToActivity(): void {
    if (this.filesToUpload) {
      const formData = new FormData();
      Array.from(this.filesToUpload).forEach((file) => {
        formData.append('files[]', file, file.name);
      });

      this.processing = true;
      this.dataService.uploadFiles(formData).subscribe((data: any) => {
        console.log(data);
        this.responseData = data;
        this.processing = false;
        this.getDataFromServer(); // Call method to retrieve data after processing
      }, (error) => {
        console.error('Error uploading files:', error);
        this.processing = false;
      });
    }
  }

  getDataFromServer(): void {
    this.dataService.getData().subscribe((data: any) => {
      console.log('Data received from server:', data);
      if (data && data.data) {
        this.parseCSVData(data.data); // Process the CSV data
      }
    }, (error) => {
      console.error('Error fetching data from server:', error);
    });
  }

  parseCSVData(csvData: string): void {
    const parsedData = parse(csvData, {
      header: true,
      skipEmptyLines: true
    });

    if (parsedData.data.length === 0) return;

    this.tableData = parsedData.data as DataRow[];
    this.displayedColumns = parsedData.meta.fields as string[];
    this.cd.detectChanges();
  }

  downloadData(): void {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Full Name,Email Address,Website,Phone Number,Skills\n" 
      + this.tableData.map(row => Object.values(row).join(",")).join("\n");
  
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "data.csv");
    document.body.appendChild(link); // Required for FF
  
    link.click();
    document.body.removeChild(link);
  }
  
}
