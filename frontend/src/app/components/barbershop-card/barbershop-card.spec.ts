import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BarbershopCard } from './barbershop-card';

describe('BarbershopCard', () => {
  let component: BarbershopCard;
  let fixture: ComponentFixture<BarbershopCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BarbershopCard],
    }).compileComponents();

    fixture = TestBed.createComponent(BarbershopCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
