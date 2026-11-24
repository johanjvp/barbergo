import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Barbershops } from './admin-barbershops';

describe('Barbershops', () => {
  let component: Barbershops;
  let fixture: ComponentFixture<Barbershops>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Barbershops],
    }).compileComponents();

    fixture = TestBed.createComponent(Barbershops);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
