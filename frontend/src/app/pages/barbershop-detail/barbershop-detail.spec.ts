import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BarbershopDetail } from './barbershop-detail';

describe('BarbershopDetail', () => {
  let component: BarbershopDetail;
  let fixture: ComponentFixture<BarbershopDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BarbershopDetail],
    }).compileComponents();

    fixture = TestBed.createComponent(BarbershopDetail);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
