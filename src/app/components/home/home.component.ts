import { Component, OnInit } from '@angular/core';
import { MatSelectModule } from '@angular/material/select';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ApiService } from '../../services/api.service';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { CommonModule } from '@angular/common';

interface Clip {
  audio_base64: string;
  text: string;
  speaker: string;
}

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

export class HomeComponent implements OnInit {
  prompt: string = '';
  mode: string = 'podcast';
  conversation: any = [];
  clips: Clip[] = [];
  currentClip: number = 0;
  audio: HTMLAudioElement = new Audio();
  text: string = '';

  constructor(private _apiservice: ApiService) {}

  getConversation(prompt: string, mode: string) {
    console.log("Submitted");
    this._apiservice.getConversation(prompt, mode).subscribe(res => {
      this.conversation = res.conversation;
      if (res.speech && Array.isArray(res.speech)) {
        this.clips = res.speech.map((clip: any) => ({
          audio_base64: clip.audio_base64 || '',
          text: clip.text || '',
          speaker: clip.speaker || ''
        }));
        console.log('Clips array after mapping:', this.clips);
        this.playNextClip();
      } else {
        console.error('Error: res.speech is not a valid array or is undefined.');
      }
    });
  }

  playNextClip() {
    if (this.currentClip < this.clips.length) {
      let clip = this.clips[this.currentClip];
      console.log('Current clip:', clip);

      if (clip && clip.audio_base64) {
        let binarystring = atob(clip.audio_base64);
        let len = binarystring.length;
        let bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
          bytes[i] = binarystring.charCodeAt(i);
        }
        const blob = new Blob([bytes], { type: 'audio/mp3' });
        const blobUrl = URL.createObjectURL(blob);
        this.audio.src = blobUrl;

        // this.audio.src = clip.audio_base64;
        this.text = clip.text;
        this.audio.play();

        // Move to the next clip when current clip ends
        this.audio.onended = () => {
          this.currentClip += 1;
          this.playNextClip();
        };
      } else {
        console.error('Audio or text is missing for the current clip:', clip);
        this.currentClip += 1;
        this.playNextClip();
      }
    } else {
      console.log('All clips played.');
    }
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

  ngOnInit() {
    // this.getConversation(this.prompt, this.mode);
  }
}
