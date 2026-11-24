import {
  ChangeDetectorRef,
  Component,
  ElementRef,
  OnDestroy,
  OnInit,
  ViewChild,
  inject
} from '@angular/core';

import Chart from 'chart.js/auto';

import {
  AdminDashboardService
} from '../../../services/admin-dashboard';

import {
  AdminDashboardResponse,
  AdminGrowthPoint
} from '../../../models/admin-dashboard';


@Component({
  selector: 'app-admin-dashboard',

  imports: [],

  templateUrl:
    './admin-dashboard.html',

  styleUrl:
    './admin-dashboard.scss'
})
export class AdminDashboard
  implements OnInit, OnDestroy {


  // =====================================================
  // CANVAS
  // =====================================================

  @ViewChild(
    'growthChartCanvas'
  )
  growthChartCanvas?:
    ElementRef<HTMLCanvasElement>;


  @ViewChild(
    'statusChartCanvas'
  )
  statusChartCanvas?:
    ElementRef<HTMLCanvasElement>;


  @ViewChild(
    'financialChartCanvas'
  )
  financialChartCanvas?:
    ElementRef<HTMLCanvasElement>;


  // =====================================================
  // DEPENDENCIAS
  // =====================================================

  private readonly dashboardService =
    inject(
      AdminDashboardService
    );


  private readonly cdr =
    inject(
      ChangeDetectorRef
    );


  // =====================================================
  // DATOS
  // =====================================================

  dashboard:
    AdminDashboardResponse | null =
      null;


  loading =
    true;


  error =
    '';


  selectedGrowth:
    'users' | 'bookings' =
      'bookings';


  // =====================================================
  // CONTADORES ANIMADOS
  // =====================================================

  animatedUsers =
    0;


  animatedBarbershops =
    0;


  animatedBookings =
    0;


  animatedReservedValue =
    0;


  private counterAnimationFrame:
    number | null =
      null;


  // =====================================================
  // GRÁFICAS
  // =====================================================

  private growthChart:
    Chart | null =
      null;


  private statusChart:
    Chart | null =
      null;


  private financialChart:
    Chart | null =
      null;


  // =====================================================
  // INICIO
  // =====================================================

  ngOnInit(): void {

    this.loadDashboard();

  }


  // =====================================================
  // DESTRUIR
  // =====================================================

  ngOnDestroy(): void {

    this.destroyCharts();


    if (
      this.counterAnimationFrame !==
      null
    ) {

      cancelAnimationFrame(
        this.counterAnimationFrame
      );

    }

  }


  // =====================================================
  // CARGAR DASHBOARD
  // =====================================================

  loadDashboard(): void {

    this.loading =
      true;


    this.error =
      '';


    this.dashboardService
      .getDashboard()
      .subscribe({

        next: (
          response
        ) => {

          this.dashboard =
            response;


          this.loading =
            false;


          this.cdr
            .detectChanges();


          // ---------------------------------------------
          // ANIMACIÓN DE CONTADORES
          // ---------------------------------------------

          this.animateCounters();


          // ---------------------------------------------
          // ESPERAR A QUE ANGULAR CREE LOS CANVAS
          // ---------------------------------------------

          setTimeout(
            () => {

              this.renderCharts();

            },
            0
          );

        },


        error: (
          error
        ) => {

          console.error(
            'Error cargando dashboard administrativo:',
            error
          );


          this.loading =
            false;


          if (
            error.status === 403
          ) {

            this.error =
              'No tienes permisos para consultar el panel administrativo.';

          }

          else if (
            error.status === 401
          ) {

            this.error =
              'Tu sesión ha expirado. Inicia sesión nuevamente.';

          }

          else {

            this.error =
              'No fue posible cargar la información administrativa.';

          }


          this.cdr
            .detectChanges();

        }

      });

  }


  // =====================================================
  // ANIMAR CONTADORES
  // =====================================================

  private animateCounters(): void {

    if (
      !this.dashboard
    ) {

      return;

    }


    if (
      this.counterAnimationFrame !==
      null
    ) {

      cancelAnimationFrame(
        this.counterAnimationFrame
      );

    }


    this.animatedUsers =
      0;


    this.animatedBarbershops =
      0;


    this.animatedBookings =
      0;


    this.animatedReservedValue =
      0;


    const usersTarget =
      this.dashboard
        .users
        .total;


    const barbershopsTarget =
      this.dashboard
        .barbershops
        .active;


    const bookingsTarget =
      this.dashboard
        .bookings
        .this_month;


    const reservedTarget =
      this.dashboard
        .financial
        .reserved_value_this_month;


    const duration =
      1100;


    const start =
      performance.now();


    const animate = (
      currentTime: number
    ) => {

      const progress =
        Math.min(
          (
            currentTime
            -
            start
          )
          /
          duration,
          1
        );


      // ---------------------------------------------
      // EASE OUT CUBIC
      // ---------------------------------------------

      const eased =
        1
        -
        Math.pow(
          1 - progress,
          3
        );


      this.animatedUsers =
        Math.round(
          usersTarget
          *
          eased
        );


      this.animatedBarbershops =
        Math.round(
          barbershopsTarget
          *
          eased
        );


      this.animatedBookings =
        Math.round(
          bookingsTarget
          *
          eased
        );


      this.animatedReservedValue =
        Math.round(
          reservedTarget
          *
          eased
        );


      this.cdr
        .detectChanges();


      if (
        progress < 1
      ) {

        this.counterAnimationFrame =
          requestAnimationFrame(
            animate
          );

      }

      else {

        this.counterAnimationFrame =
          null;

      }

    };


    this.counterAnimationFrame =
      requestAnimationFrame(
        animate
      );

  }


  // =====================================================
  // CAMBIAR CRECIMIENTO
  // =====================================================

  showGrowth(
    type:
      'users'
      |
      'bookings'
  ): void {

    if (
      this.selectedGrowth ===
      type
    ) {

      return;

    }


    this.selectedGrowth =
      type;


    this.renderGrowthChart();

  }


  // =====================================================
  // DATOS CRECIMIENTO
  // =====================================================

  get growthData():
    AdminGrowthPoint[] {

    if (
      !this.dashboard
    ) {

      return [];

    }


    if (
      this.selectedGrowth ===
      'users'
    ) {

      return (
        this.dashboard
          .growth
          .users
      );

    }


    return (
      this.dashboard
        .growth
        .bookings
    );

  }


  // =====================================================
  // RENDERIZAR TODAS
  // =====================================================

  private renderCharts(): void {

    this.renderGrowthChart();

    this.renderStatusChart();

    this.renderFinancialChart();

  }


  // =====================================================
  // GRÁFICA CRECIMIENTO
  // =====================================================

  private renderGrowthChart(): void {

    if (
      !this.dashboard
      ||
      !this.growthChartCanvas
    ) {

      return;

    }


    this.growthChart
      ?.destroy();


    const canvas =
      this.growthChartCanvas
        .nativeElement;


    const context =
      canvas
        .getContext(
          '2d'
        );


    if (
      !context
    ) {

      return;

    }


    const gradient =
      context
        .createLinearGradient(
          0,
          0,
          0,
          320
        );


    if (
      this.selectedGrowth ===
      'bookings'
    ) {

      gradient
        .addColorStop(
          0,
          'rgba(59, 130, 246, 0.35)'
        );


      gradient
        .addColorStop(
          1,
          'rgba(59, 130, 246, 0.01)'
        );

    }

    else {

      gradient
        .addColorStop(
          0,
          'rgba(139, 92, 246, 0.32)'
        );


      gradient
        .addColorStop(
          1,
          'rgba(139, 92, 246, 0.01)'
        );

    }


    const labels =
      this.growthData
        .map(
          item =>
            this.formatShortDate(
              item.date
            )
        );


    const values =
      this.growthData
        .map(
          item =>
            item.total
        );


    const lineColor =
      this.selectedGrowth ===
      'bookings'
        ?
        '#3b82f6'
        :
        '#8b5cf6';


    this.growthChart =
      new Chart(
        canvas,
        {

          type:
            'line',

          data: {

            labels,

            datasets: [

              {

                label:
                  this.selectedGrowth ===
                  'bookings'
                    ?
                    'Reservas'
                    :
                    'Usuarios',

                data:
                  values,

                borderColor:
                  lineColor,

                backgroundColor:
                  gradient,

                fill:
                  true,

                borderWidth:
                  3,

                pointRadius:
                  2,

                pointHoverRadius:
                  6,

                pointBackgroundColor:
                  '#ffffff',

                pointBorderColor:
                  lineColor,

                pointBorderWidth:
                  2,

                tension:
                  0.38

              }

            ]

          },


          options: {

            responsive:
              true,

            maintainAspectRatio:
              false,


            interaction: {

              intersect:
                false,

              mode:
                'index'

            },


            animation: {

              duration:
                900,

              easing:
                'easeOutQuart'

            },


            plugins: {

              legend: {
                display:
                  false
              },


              tooltip: {

                backgroundColor:
                  '#111827',

                titleColor:
                  '#ffffff',

                bodyColor:
                  '#e5e7eb',

                padding:
                  12,

                displayColors:
                  false,

                cornerRadius:
                  10

              }

            },


            scales: {

              x: {

                grid: {
                  display:
                    false
                },

                border: {
                  display:
                    false
                },

                ticks: {

                  color:
                    '#9ca3af',

                  font: {
                    size:
                      9
                  },

                  maxRotation:
                    0,

                  autoSkip:
                    true,

                  maxTicksLimit:
                    7

                }

              },


              y: {

                beginAtZero:
                  true,

                border: {
                  display:
                    false
                },

                grid: {

                  color:
                    'rgba(15, 23, 42, 0.055)'

                },

                ticks: {

                  precision:
                    0,

                  color:
                    '#9ca3af',

                  font: {
                    size:
                      9
                  }

                }

              }

            }

          }

        }
      );

  }


  // =====================================================
  // GRÁFICA ESTADOS
  // =====================================================

  private renderStatusChart(): void {

    if (
      !this.dashboard
      ||
      !this.statusChartCanvas
    ) {

      return;

    }


    this.statusChart
      ?.destroy();


    const bookings =
      this.dashboard
        .bookings;


    this.statusChart =
      new Chart(
        this.statusChartCanvas
          .nativeElement,
        {

          type:
            'doughnut',

          data: {

            labels: [

              'Pendientes',
              'Confirmadas',
              'En proceso',
              'Completadas',
              'Canceladas',
              'No-show',
              'Rechazadas'

            ],

            datasets: [

              {

                data: [

                  bookings.pending,
                  bookings.confirmed,
                  bookings.in_progress,
                  bookings.completed,
                  bookings.cancelled,
                  bookings.no_show,
                  bookings.rejected

                ],

                backgroundColor: [

                  '#f59e0b',
                  '#3b82f6',
                  '#8b5cf6',
                  '#10b981',
                  '#ef4444',
                  '#64748b',
                  '#ec4899'

                ],

                borderWidth:
                  0,

                hoverOffset:
                  10,

                spacing:
                  3,

                borderRadius:
                  5

              }

            ]

          },


          options: {

            responsive:
              true,

            maintainAspectRatio:
              false,

            cutout:
              '72%',


            animation: {

              animateRotate:
                true,

              animateScale:
                true,

              duration:
                1000

            },


            plugins: {

              legend: {

                position:
                  'bottom',

                labels: {

                  usePointStyle:
                    true,

                  pointStyle:
                    'circle',

                  padding:
                    17,

                  color:
                    '#6b7280',

                  font: {
                    size:
                      10
                  }

                }

              },


              tooltip: {

                backgroundColor:
                  '#111827',

                padding:
                  11,

                displayColors:
                  true,

                cornerRadius:
                  10

              }

            }

          }

        }
      );

  }


  // =====================================================
  // GRÁFICA FINANCIERA
  // =====================================================

  private renderFinancialChart(): void {

    if (
      !this.dashboard
      ||
      !this.financialChartCanvas
    ) {

      return;

    }


    this.financialChart
      ?.destroy();


    const simulation =
      this.dashboard
        .financial_simulation;


    this.financialChart =
      new Chart(
        this.financialChartCanvas
          .nativeElement,
        {

          type:
            'bar',

          data: {

            labels: [

              'GMV',
              'Completado',
              'BarberGo',
              'Barberías',
              'Potencial perdido'

            ],

            datasets: [

              {

                label:
                  'COP',

                data: [

                  simulation
                    .gross_booking_value,

                  simulation
                    .completed_value,

                  simulation
                    .projected_platform_revenue,

                  simulation
                    .projected_barbershop_payout,

                  simulation
                    .lost_value

                ],

                backgroundColor: [

                  '#3b82f6',
                  '#10b981',
                  '#8b5cf6',
                  '#06b6d4',
                  '#ef4444'

                ],

                borderRadius:
                  8,

                borderSkipped:
                  false,

                barThickness:
                  26

              }

            ]

          },


          options: {

            indexAxis:
              'y',

            responsive:
              true,

            maintainAspectRatio:
              false,


            animation: {

              duration:
                950,

              easing:
                'easeOutQuart'

            },


            plugins: {

              legend: {
                display:
                  false
              },


              tooltip: {

                backgroundColor:
                  '#111827',

                padding:
                  11,

                displayColors:
                  true,

                cornerRadius:
                  10,

                callbacks: {

                  label: (
                    context
                  ) => {

                    const value =
                      Number(
                        context.raw
                        ??
                        0
                      );


                    return (
                      ' '
                      +
                      this.formatCurrency(
                        value
                      )
                    );

                  }

                }

              }

            },


            scales: {

              x: {

                beginAtZero:
                  true,

                border: {
                  display:
                    false
                },

                grid: {

                  color:
                    'rgba(255, 255, 255, 0.06)'

                },

                ticks: {

                  color:
                    '#8b93a1',

                  font: {
                    size:
                      9
                  },

                  callback: (
                    value
                  ) => {

                    const amount =
                      Number(
                        value
                      );


                    if (
                      amount >=
                      1000000
                    ) {

                      return (
                        '$'
                        +
                        (
                          amount
                          /
                          1000000
                        )
                        .toFixed(
                          1
                        )
                        +
                        'M'
                      );

                    }


                    if (
                      amount >=
                      1000
                    ) {

                      return (
                        '$'
                        +
                        Math.round(
                          amount
                          /
                          1000
                        )
                        +
                        'k'
                      );

                    }


                    return (
                      '$'
                      +
                      amount
                    );

                  }

                }

              },


              y: {

                border: {
                  display:
                    false
                },

                grid: {
                  display:
                    false
                },

                ticks: {

                  color:
                    '#d1d5db',

                  font: {

                    size:
                      10,

                    weight:
                      600

                  }

                }

              }

            }

          }

        }
      );

  }


  // =====================================================
  // DESTRUIR GRÁFICAS
  // =====================================================

  private destroyCharts(): void {

    this.growthChart
      ?.destroy();


    this.statusChart
      ?.destroy();


    this.financialChart
      ?.destroy();


    this.growthChart =
      null;


    this.statusChart =
      null;


    this.financialChart =
      null;

  }


  // =====================================================
  // MONEDA
  // =====================================================

  formatCurrency(
    value:
      number
      |
      null
      |
      undefined
  ): string {

    return new Intl
      .NumberFormat(
        'es-CO',
        {
          style:
            'currency',

          currency:
            'COP',

          maximumFractionDigits:
            0
        }
      )
      .format(
        Number(
          value
          ??
          0
        )
      );

  }


  // =====================================================
  // NÚMERO
  // =====================================================

  formatNumber(
    value:
      number
      |
      null
      |
      undefined
  ): string {

    return new Intl
      .NumberFormat(
        'es-CO'
      )
      .format(
        Number(
          value
          ??
          0
        )
      );

  }


  // =====================================================
  // PORCENTAJE
  // =====================================================

  formatPercentage(
    value:
      number
      |
      null
      |
      undefined
  ): string {

    return (
      Number(
        value
        ??
        0
      )
      .toFixed(
        1
      )
      +
      '%'
    );

  }


  // =====================================================
  // FECHA
  // =====================================================

  formatShortDate(
    value: string
  ): string {

    if (
      !value
    ) {

      return '';

    }


    const parts =
      value
        .split('-')
        .map(
          Number
        );


    if (
      parts.length !== 3
    ) {

      return value;

    }


    const currentDate =
      new Date(
        parts[0],
        parts[1] - 1,
        parts[2]
      );


    return new Intl
      .DateTimeFormat(
        'es-CO',
        {
          day:
            '2-digit',

          month:
            'short'
        }
      )
      .format(
        currentDate
      );

  }

}
