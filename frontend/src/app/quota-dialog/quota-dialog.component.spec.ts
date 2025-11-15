import { ComponentFixture, TestBed } from '@angular/core/testing';

import { QuotaDialogComponent } from './quota-dialog.component';

describe('QuotaDialogComponent', () => {
  let component: QuotaDialogComponent;
  let fixture: ComponentFixture<QuotaDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [QuotaDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(QuotaDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
