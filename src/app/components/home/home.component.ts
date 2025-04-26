import { Component } from '@angular/core';
// import { RouterLink, RouterModule, RouterOutlet } from '@angular/router';
import { MatSelectModule } from '@angular/material/select';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ApiService } from '../../services/api.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home',
  standalone: true,
  providers: [ApiService],
  imports: [
    // RouterModule,
    // RouterLink,
    // RouterOutlet,
    MatSelectModule,
    FontAwesomeModule,
    HttpClientModule,
    CommonModule
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  prompt: string = '';
  conversation: any = [];
  speech_generated: string = 'False';

  constructor(
    private _apiservice: ApiService,
    private http: HttpClient
  ) {}

  getConversation(prompt: string, event?: Event) {
    if (event) {
      event.preventDefault();
    }
    console.log("Submitted");
    this._apiservice.getConversation(prompt).subscribe(res => {
      console.log('Response: ', res);
      this.conversation = res.conversation;
      console.log('conversation: ', this.conversation);
      this.speech_generated = res.speech_generated;
      console.log('speech_generated: ', this.speech_generated);
    });
  }

}
