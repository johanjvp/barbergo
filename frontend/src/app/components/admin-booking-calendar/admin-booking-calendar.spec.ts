import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminBookingCalendar } from './admin-booking-calendar';

describe('AdminBookingCalendar', () => {
  let component: AdminBookingCalendar;
  let fixture: ComponentFixture<AdminBookingCalendar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminBookingCalendar],
    }).compileComponents();

    fixture = TestBed.createComponent(AdminBookingCalendar);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
