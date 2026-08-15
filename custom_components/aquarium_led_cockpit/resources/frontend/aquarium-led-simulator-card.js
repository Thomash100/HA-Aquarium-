class AquariumLedSimulatorCard extends HTMLElement {
  setConfig(config) {
    this.config = {
      title: "Aquarium LED Simulation",
      status_entity: "sensor.aquarium_status",
      ...config,
    };
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getCardSize() {
    return 4;
  }

  render() {
    if (!this.config || !this._hass) {
      return;
    }

    const state = this._hass.states[this.config.status_entity];
    if (!state) {
      this.innerHTML = `
        <ha-card>
          <div class="alc-wrap">
            ${this.styles()}
            <div class="alc-title">${this.escape(this.config.title)}</div>
            <div class="alc-empty">Status-Entitaet nicht gefunden: ${this.escape(this.config.status_entity)}</div>
          </div>
        </ha-card>
      `;
      return;
    }

    const attr = state.attributes || {};
    const phase = this.phaseLabel(attr.phase || state.state);
    const rgbw = Array.isArray(attr.rgbw) ? attr.rgbw : [15, 30, 90, 0];
    const target = Number(attr.target_pct || 0);
    const base = Number(attr.base_pct || target || 0);
    const white = Number(attr.white_pct || 0);
    const currentTime = attr.time || "--:--";
    const sunrise = attr.sunrise || "06:00";
    const sunset = attr.sunset || "18:00";
    const curve = this.buildCurve(sunrise, sunset, base, target);
    const rgb = `rgb(${rgbw[0] || 0}, ${rgbw[1] || 0}, ${rgbw[2] || 0})`;
    const whiteAlpha = Math.max(0.08, Math.min(0.85, (rgbw[3] || 0) / 255));

    this.innerHTML = `
      <ha-card>
        <div class="alc-wrap">
          ${this.styles()}
          <div class="alc-head">
            <div>
              <div class="alc-title">${this.escape(this.config.title)}</div>
              <div class="alc-sub">${this.escape(phase)} um ${this.escape(currentTime)}</div>
            </div>
            <div class="alc-badge">${target}%</div>
          </div>

          <div class="alc-horizon" style="--alc-rgb: ${rgb}; --alc-white: ${whiteAlpha};">
            <div class="alc-sun" style="left: ${this.sunPosition(currentTime, sunrise, sunset)}%;"></div>
            <div class="alc-now" style="left: ${this.minutePercent(currentTime)}%;"></div>
          </div>

          <svg class="alc-chart" viewBox="0 0 320 96" role="img" aria-label="24-Stunden-Lichtkurve">
            <defs>
              <linearGradient id="alc-fill" x1="0" x2="0" y1="0" y2="1">
                <stop offset="0%" stop-color="${rgb}" stop-opacity="0.44"></stop>
                <stop offset="100%" stop-color="${rgb}" stop-opacity="0.06"></stop>
              </linearGradient>
            </defs>
            <path d="${curve.fill}" fill="url(#alc-fill)"></path>
            <path d="${curve.line}" fill="none" stroke="${rgb}" stroke-width="3" stroke-linecap="round"></path>
            <line x1="${this.minutePercent(currentTime) * 3.2}" y1="8" x2="${this.minutePercent(currentTime) * 3.2}" y2="88" class="alc-chart-now"></line>
          </svg>

          <div class="alc-times">
            <span>Sonnenaufgang ${this.escape(sunrise)}</span>
            <span>Sonnenuntergang ${this.escape(sunset)}</span>
          </div>

          <div class="alc-grid">
            ${this.metric("Basis", `${base}%`)}
            ${this.metric("Weiss", `${white}%`)}
            ${this.metric("Preis", this.formatValue(attr.price))}
            ${this.metric("Preis-Dimmung", this.formatPercent(attr.price_dimming_pct))}
            ${this.metric("Speicher", this.formatPercent(attr.battery_soc))}
            ${this.metric("Preisregel", attr.price_ignored ? "Ignoriert" : "Aktiv")}
            ${this.metric("Solar", this.formatPower(attr.solar_power))}
            ${this.metric("Sonne regional", attr.regional_sun ? "Ja" : "Nein")}
            ${this.metric("Wolken", `${attr.cloudiness_pct ?? "-"}%`)}
          </div>

          <div class="alc-controls">
            ${this.controlButton("simulation_switch", "Simulation ein", "turn_on")}
            ${this.controlButton("time_lapse_switch", "Zeitraffer starten", "turn_on")}
            ${this.controlButton("time_lapse_switch", "Zeitraffer stoppen", "turn_off")}
          </div>
        </div>
      </ha-card>
    `;

    this.querySelectorAll("[data-domain]").forEach((button) => {
      button.addEventListener("click", () => {
        this._hass.callService(button.dataset.domain, button.dataset.service, {
          entity_id: button.dataset.entity,
        });
      });
    });
  }

  styles() {
    return `
      <style>
        .alc-wrap { padding: 18px; color: var(--primary-text-color); }
        .alc-head { align-items: center; display: flex; justify-content: space-between; gap: 16px; }
        .alc-title { font-size: 18px; font-weight: 600; line-height: 1.25; }
        .alc-sub { color: var(--secondary-text-color); font-size: 13px; margin-top: 3px; }
        .alc-badge { border-radius: 999px; background: var(--primary-color); color: var(--text-primary-color); font-weight: 700; min-width: 54px; padding: 8px 10px; text-align: center; }
        .alc-empty { color: var(--error-color); margin-top: 10px; }
        .alc-horizon { background: linear-gradient(90deg, #10172f 0%, #f18f45 24%, var(--alc-rgb) 50%, #d95d3d 76%, #10172f 100%); border-radius: 8px; height: 76px; margin-top: 18px; overflow: hidden; position: relative; }
        .alc-horizon::after { background: radial-gradient(circle at 50% 42%, rgba(255,255,255,var(--alc-white)), transparent 34%), linear-gradient(180deg, transparent 45%, rgba(0,0,0,0.26)); content: ""; inset: 0; position: absolute; }
        .alc-sun { background: #ffd36a; border-radius: 999px; box-shadow: 0 0 24px rgba(255, 211, 106, 0.74); height: 22px; position: absolute; top: 18px; transform: translateX(-50%); width: 22px; z-index: 1; }
        .alc-now { background: rgba(255,255,255,0.8); bottom: 0; position: absolute; top: 0; width: 2px; z-index: 2; }
        .alc-chart { display: block; height: 96px; margin-top: 14px; width: 100%; }
        .alc-chart-now { stroke: var(--secondary-text-color); stroke-dasharray: 3 4; stroke-width: 1.5; }
        .alc-times { color: var(--secondary-text-color); display: flex; font-size: 12px; justify-content: space-between; gap: 12px; margin-top: 4px; }
        .alc-grid { display: grid; gap: 8px; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 14px; }
        .alc-metric { background: var(--secondary-background-color); border-radius: 8px; padding: 9px 10px; min-width: 0; }
        .alc-metric-label { color: var(--secondary-text-color); font-size: 11px; line-height: 1.2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .alc-metric-value { font-size: 15px; font-weight: 600; line-height: 1.25; margin-top: 3px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .alc-controls { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
        .alc-controls button { align-items: center; background: var(--primary-color); border: 0; border-radius: 6px; color: var(--text-primary-color); cursor: pointer; display: inline-flex; font: inherit; font-size: 13px; min-height: 36px; padding: 0 12px; }
        @media (max-width: 520px) {
          .alc-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
          .alc-times { flex-direction: column; gap: 2px; }
          .alc-controls button { flex: 1 1 100%; justify-content: center; }
        }
      </style>
    `;
  }

  metric(label, value) {
    return `
      <div class="alc-metric">
        <div class="alc-metric-label">${this.escape(label)}</div>
        <div class="alc-metric-value">${this.escape(value)}</div>
      </div>
    `;
  }

  controlButton(configKey, label, service) {
    const entity = this.config[configKey];
    if (!entity) {
      return "";
    }
    return `<button data-domain="switch" data-service="${service}" data-entity="${this.escape(entity)}">${this.escape(label)}</button>`;
  }

  buildCurve(sunrise, sunset, base, target) {
    const sunriseMinute = this.parseMinute(sunrise, 360);
    const sunsetMinute = this.parseMinute(sunset, 1080);
    const dayPct = Math.max(base, target, 70);
    const nightPct = 3;
    const points = [];

    for (let index = 0; index <= 96; index += 1) {
      const minute = index * 15;
      const pct = this.profileAt(minute, sunriseMinute, sunsetMinute, nightPct, dayPct);
      const x = (index / 96) * 320;
      const y = 88 - (pct / 100) * 72;
      points.push([x, y]);
    }

    const line = points.map((point, index) => `${index === 0 ? "M" : "L"} ${point[0].toFixed(1)} ${point[1].toFixed(1)}`).join(" ");
    const fill = `${line} L 320 92 L 0 92 Z`;
    return { line, fill };
  }

  profileAt(minute, sunrise, sunset, night, day) {
    const sunriseDuration = 120;
    const sunsetDuration = 150;
    if (minute >= sunrise && minute < sunrise + sunriseDuration) {
      return night + ((day - night) * ((minute - sunrise) / sunriseDuration));
    }
    if (minute >= sunrise + sunriseDuration && minute < sunset) {
      return day;
    }
    if (minute >= sunset && minute < sunset + sunsetDuration) {
      return day + ((night - day) * ((minute - sunset) / sunsetDuration));
    }
    return night;
  }

  sunPosition(time, sunrise, sunset) {
    const minute = this.parseMinute(time, 720);
    const rise = this.parseMinute(sunrise, 360);
    const set = this.parseMinute(sunset, 1080);
    if (minute <= rise) {
      return 8;
    }
    if (minute >= set) {
      return 92;
    }
    return 8 + ((minute - rise) / Math.max(1, set - rise)) * 84;
  }

  minutePercent(value) {
    return (this.parseMinute(value, 0) / 1440) * 100;
  }

  parseMinute(value, fallback) {
    const match = String(value || "").match(/^(\d{1,2}):(\d{2})$/);
    if (!match) {
      return fallback;
    }
    return Math.max(0, Math.min(1439, Number(match[1]) * 60 + Number(match[2])));
  }

  phaseLabel(value) {
    const labels = {
      sunrise: "Sonnenaufgang",
      day: "Tag",
      sunset: "Sonnenuntergang",
      night: "Nacht",
      idle: "Warten",
    };
    return labels[value] || value || "Unbekannt";
  }

  formatPercent(value) {
    if (value === undefined || value === null || value === "-") {
      return "-";
    }
    return `${Math.round(Number(value))}%`;
  }

  formatPower(value) {
    if (value === undefined || value === null || value === "-") {
      return "-";
    }
    return `${Math.round(Number(value))} W`;
  }

  formatValue(value) {
    if (value === undefined || value === null || value === "") {
      return "-";
    }
    return String(value);
  }

  escape(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }
}

customElements.define("aquarium-led-simulator-card", AquariumLedSimulatorCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: "aquarium-led-simulator-card",
  name: "Aquarium LED Simulator",
  description: "Zeigt Sonnenaufgang, Sonnenuntergang, Zielhelligkeit und Teststeuerung fuer Aquarium LED Cockpit.",
});
