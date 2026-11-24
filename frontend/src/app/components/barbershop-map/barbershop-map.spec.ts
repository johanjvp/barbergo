import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BarbershopMap } from './barbershop-map';

describe('BarbershopMap', () => {
  let component: BarbershopMap;
  let fixture: ComponentFixture<BarbershopMap>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BarbershopMap],
    }).compileComponents();

    fixture = TestBed.createComponent(BarbershopMap);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
