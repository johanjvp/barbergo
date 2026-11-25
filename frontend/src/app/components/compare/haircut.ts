import { Component, Input } from '@angular/core';

/** Ilustración vectorial de un mismo retrato antes / después de un corte. */
@Component({
  selector: 'app-haircut',
  standalone: true,
  template: `
    <svg viewBox="0 0 400 250" preserveAspectRatio="xMidYMid slice" role="img"
         [attr.aria-label]="state === 'before' ? 'Antes del corte' : 'Después del corte'">
      <defs>
        <linearGradient [attr.id]="'bg' + state" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" [attr.stop-color]="state === 'before' ? '#1b3a44' : '#0f766e'"/>
          <stop offset="1" [attr.stop-color]="state === 'before' ? '#0b1f2a' : '#134e4a'"/>
        </linearGradient>
        <linearGradient [attr.id]="'skin' + state" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#e8b48f"/><stop offset="1" stop-color="#d49a73"/>
        </linearGradient>
        <linearGradient [attr.id]="'fade' + state" x1="0" y1="1" x2="0" y2="0">
          <stop offset="0" stop-color="#2a1d17" stop-opacity="0"/>
          <stop offset="1" stop-color="#2a1d17" stop-opacity=".95"/>
        </linearGradient>
      </defs>

      <rect width="400" height="250" [attr.fill]="'url(#bg' + state + ')'"/>
      <circle cx="320" cy="50" r="70" fill="#fff" opacity=".05"/>
      <circle cx="70" cy="210" r="90" fill="#fff" opacity=".04"/>

      <!-- hombros y camisa -->
      <path d="M60 250 C66 205 120 188 200 188 C280 188 334 205 340 250Z" fill="#26323b"/>
      <path d="M172 188 L200 222 L228 188 Z" fill="#e8eef0"/>
      <path d="M172 188 L158 196 L190 232Z M228 188 L242 196 L210 232Z" fill="#cdd8dc"/>

      <!-- cuello -->
      <path d="M174 140 L174 196 C186 210 214 210 226 196 L226 140Z" [attr.fill]="'url(#skin' + state + ')'"/>
      <path d="M174 170 C190 186 210 186 226 170 L226 150 L174 150Z" fill="#000" opacity=".12"/>

      <!-- orejas -->
      <ellipse cx="152" cy="108" rx="9" ry="14" fill="#d9a07a"/>
      <ellipse cx="248" cy="108" rx="9" ry="14" fill="#d9a07a"/>

      <!-- cara -->
      <path d="M152 92 C152 50 176 36 200 36 C224 36 248 50 248 92 L248 118 C248 150 226 170 200 170 C174 170 152 150 152 118Z"
            [attr.fill]="'url(#skin' + state + ')'"/>

      @if (state === 'before') {
        <!-- barba descuidada -->
        <path d="M152 112 C150 150 172 178 200 180 C228 178 250 150 248 112 C244 134 232 146 220 150 C212 144 188 144 180 150 C168 146 156 134 152 112Z" fill="#3a2a22" opacity=".85"/>
        <g stroke="#3a2a22" stroke-width="2.2" stroke-linecap="round" opacity=".9">
          <path d="M160 160 l-6 8 M170 172 l-4 9 M186 180 l-2 9 M200 182 l0 10 M214 180 l2 9 M230 172 l4 9 M240 160 l6 8"/>
        </g>
        <!-- pelo largo y desordenado -->
        <path d="M138 98 C124 52 150 14 200 12 C252 14 278 52 262 98 C262 74 250 58 232 54 C226 64 212 66 200 62 C186 66 172 64 168 54 C150 58 138 74 138 98Z" fill="#3a2a22"/>
        <path d="M140 100 C128 120 134 150 148 160 C146 140 148 120 152 104Z M260 100 C272 120 266 150 252 160 C254 140 252 120 248 104Z" fill="#3a2a22"/>
        <g stroke="#3a2a22" stroke-width="5" stroke-linecap="round" fill="none">
          <path d="M170 24 C160 6 176 2 182 14"/><path d="M200 14 C196 -4 212 -4 214 12"/>
          <path d="M232 22 C246 8 258 20 246 30"/><path d="M146 52 C132 44 128 60 140 66"/>
          <path d="M262 56 C276 52 280 68 266 72"/>
        </g>
        <path d="M160 70 C172 56 196 52 214 58 C226 62 236 66 240 74" stroke="#5a4236" stroke-width="3" fill="none" opacity=".7" stroke-linecap="round"/>
      } @else {
        <!-- fade limpio -->
        <path d="M150 96 C148 54 174 34 200 34 C226 34 252 54 250 96 C246 76 236 62 218 58 C208 54 192 54 182 58 C164 62 154 76 150 96Z" fill="#2a1d17"/>
        <path d="M150 100 C148 82 152 70 158 64 L170 70 L166 104Z M250 100 C252 82 248 70 242 64 L230 70 L234 104Z" [attr.fill]="'url(#fade' + state + ')'"/>
        <path d="M168 44 C186 36 214 36 232 44" stroke="#4a3328" stroke-width="3" fill="none" stroke-linecap="round" opacity=".8"/>
        <path d="M176 52 C190 46 210 46 224 52" stroke="#4a3328" stroke-width="2" fill="none" stroke-linecap="round" opacity=".6"/>
        <!-- barba perfilada -->
        <path d="M153 118 C156 146 174 170 200 172 C226 170 244 146 247 118 C243 140 230 150 218 152 C210 146 190 146 182 152 C170 150 157 140 153 118Z" fill="#2a1d17" opacity=".78"/>
        <path d="M184 140 C192 136 208 136 216 140" stroke="#d49a73" stroke-width="2.4" fill="none" stroke-linecap="round"/>
        <path d="M153 118 C156 146 174 170 200 172 C226 170 244 146 247 118" stroke="#1d130e" stroke-width="1.4" fill="none" opacity=".6"/>
      }

      <!-- rostro -->
      <path d="M170 90 Q180 84 190 90 M210 90 Q220 84 230 90" stroke="#2a1d17" stroke-width="4" fill="none" stroke-linecap="round"/>
      <ellipse cx="180" cy="102" rx="5" ry="3.4" fill="#2a1d17"/><ellipse cx="220" cy="102" rx="5" ry="3.4" fill="#2a1d17"/>
      <circle cx="181.5" cy="101" r="1.2" fill="#fff"/><circle cx="221.5" cy="101" r="1.2" fill="#fff"/>
      <path d="M200 104 C196 116 194 122 200 124 C206 122 204 116 200 104" stroke="#b9805c" stroke-width="2" fill="none" stroke-linecap="round"/>
      @if (state === 'before') {
        <path d="M188 138 Q200 142 212 138" stroke="#7a4a3a" stroke-width="3" fill="none" stroke-linecap="round"/>
      } @else {
        <path d="M186 136 Q200 148 214 136" stroke="#fff" stroke-width="3.2" fill="none" stroke-linecap="round"/>
        <path d="M186 136 Q200 148 214 136 Q200 142 186 136Z" fill="#fff" opacity=".9"/>
        <!-- destello -->
        <path d="M312 70 l4 12 12 4 -12 4 -4 12 -4 -12 -12 -4 12 -4Z" fill="#fde68a"/>
        <path d="M82 120 l3 8 8 3 -8 3 -3 8 -3 -8 -8 -3 8 -3Z" fill="#5eead4"/>
      }
    </svg>
  `,
  styles: [`
    :host { display: block; width: 100%; height: 100%; }
    svg { width: 100%; height: 100%; display: block; }
  `]
})
export class Haircut {
  @Input() state: 'before' | 'after' = 'before';
}
