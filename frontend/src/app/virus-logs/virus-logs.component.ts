import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { MatTableModule } from '@angular/material/table';
import { Location } from '@angular/common';


@Component({
  selector: 'app-virus-logs',
  standalone: true,
  imports: [CommonModule, MatTableModule],
  templateUrl: './virus-logs.component.html',
  styleUrl: './virus-logs.component.css'
})
export class VirusLogsComponent implements OnInit {

  logs: any[] = [];
  displayedColumns = ['timestamp', 'user', 'filename', 'detected', 'result_detail'];



  constructor(private http: HttpClient, private location: Location ) {}

  goBack() {
  this.location.back();
}
  ngOnInit(): void {

    this.loadLogs();
  }
toggleExpand(row: any) {
  row._expanded = !row._expanded;
}
  loadLogs() {
    const token = sessionStorage.getItem("token");

    this.http.get("https://guvenli-dosya-yukleme.onrender.com/api/virus_logs/", {
      headers: new HttpHeaders({ "Authorization": `Token ${token}` })
    }).subscribe({
      next: (res: any) => {
        this.logs = res;
      },
      error: () => alert("Virüs logları alınamadı!")
    });
  }
}
