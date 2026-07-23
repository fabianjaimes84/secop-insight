import { Proceso } from '../../../../core/models/proceso';
import { Component, Input } from '@angular/core';
import { Card } from '../../../../shared/ui/card/card';


@Component({
  selector: 'app-results-table',
  standalone: true,
  imports: [Card],
  templateUrl: './results-table.html',
  styleUrl: './results-table.scss',
})
export class ResultsTable {
  @Input()
  processes: Proceso[] = [];
}
