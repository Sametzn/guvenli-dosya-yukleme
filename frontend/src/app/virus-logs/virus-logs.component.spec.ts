import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VirusLogsComponent } from './virus-logs.component';

describe('VirusLogsComponent', () => {
  let component: VirusLogsComponent;
  let fixture: ComponentFixture<VirusLogsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VirusLogsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VirusLogsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
