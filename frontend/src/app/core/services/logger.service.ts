import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class LoggerService {

  debug(message: unknown, ...optionalParams: unknown[]): void {
    console.debug(message, ...optionalParams);
  }

  info(message: unknown, ...optionalParams: unknown[]): void {
    console.info(message, ...optionalParams);
  }

  warn(message: unknown, ...optionalParams: unknown[]): void {
    console.warn(message, ...optionalParams);
  }

  error(message: unknown, ...optionalParams: unknown[]): void {
    console.error(message, ...optionalParams);
  }

}