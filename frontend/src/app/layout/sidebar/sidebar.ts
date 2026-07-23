import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';

import {
  faGaugeHigh,
  faMagnifyingGlass,
  faBookmark,
  faFileLines,
  faBrain,
  faGear,
  faCircleQuestion,
} from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [
    RouterLink,
    FontAwesomeModule
  ],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
})

export class Sidebar {
  faGaugeHigh = faGaugeHigh;
  faMagnifyingGlass = faMagnifyingGlass;
  faBookmark = faBookmark;
  faFileLines = faFileLines;
  faBrain = faBrain;
  faGear = faGear;
  faCircleQuestion = faCircleQuestion;
}