import { Component } from '@angular/core';
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
  mode: string = 'podcast';
  conversation: any = [
    {
        "Person1": "Hey, you know how computers organize data sometimes using these things called binary trees"
    },
    {
        "Person2": "Binary trees, yeah I've heard the term but not really sure what they are"
    },
    {
        "Person1": "Okay, so imagine a family tree but each person only has at most two children"
    },
    {
        "Person2": "Gotcha, like a node with two branches"
    },
    {
        "Person1": "Exactly Each node in the tree holds some data, and it has a left child and a right child"
    },
    {
        "Person2": "So what determines where data goes, left or right"
    },
    {
        "Person1": "That's based on a rule Usually, it's about comparing values If the new value is less than the parent node's value, it goes left If it's greater, it goes right"
    },
    {
        "Person2": "Alright, makes sense, smaller goes left, bigger goes right"
    },
    {
        "Person1": "Yep And this continues down the tree until you find an empty spot to place your data"
    },
    {
        "Person2": "And how does this help with finding things faster"
    },
    {
        "Person1": "Well, because it's organized this way, you can quickly narrow your search Imagine looking for a name in a phone book If the name is alphabetically before the one you're looking at, you know to only check the left side of the tree"
    },
    {
        "Person2": "Ah, so it cuts down the search space in half each time"
    },
    {
        "Person1": "Precisely That makes searching very efficient Compared to, say, just looking through a list one by one"
    },
    {
        "Person2": "Okay, I think I get it So it's all about creating an organized structure that makes searching and sorting faster. Pretty neat!"
    }
];
  speech_generated: string = 'False';
  currentLineIndex: number = 0;

  constructor(private _apiservice: ApiService) {}

  getConversation(prompt: string, mode: string) {
    console.log("Submitted");
    this._apiservice.getConversation(prompt, mode).subscribe(res => {
      console.log('Response: ', res);
      this.conversation = res.conversation;
      console.log('conversation: ', this.conversation);
      this.speech_generated = res.speech_generated;
      console.log('speech_generated: ', this.speech_generated);
    });
  }

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    console.log('File selected: ', formData);

    this.getConversation(this.prompt, 'pdf');
  }

  getSpeaker(line: any): string {
    return Object.keys(line)[0];
  }
  
  getSpeech(line: any): string {
    return line[this.getSpeaker(line)];
  }

  nextLine() {
    if (this.currentLineIndex < this.conversation.length - 1) {
      this.currentLineIndex++;
    }
  }

}
