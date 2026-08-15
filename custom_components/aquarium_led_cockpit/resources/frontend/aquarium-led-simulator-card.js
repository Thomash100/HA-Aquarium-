class AquariumLedSimulatorCard extends HTMLElement {
  setConfig(config) {
    this.config = {
      title: "Aquarium LED Simulation",
      status_entity: "sensor.aquarium_status",
      ...config,
    };
    this._timeline = this._timeline || {
      batteryHistory: [],
      error: "",
      key: "",
      loadedAt: 0,
      loading: false,
      priceForecast: [],
      priceHistory: [],
    };
  }

  set hass(hass) {
    this._hass = hass;
    this.render();
  }

  getCardSize() {
    return 10;
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
    const sunriseDuration = Number(attr.sunrise_duration_minutes ?? 60);
    const sunsetDuration = Number(attr.sunset_duration_minutes ?? 90);
    const dayBrightness = Number(attr.day_brightness_pct ?? Math.max(base, target, 70));
    const nightBrightness = Number(attr.night_brightness_pct ?? 3);
    const curve = this.buildCurve(
      sunrise,
      sunset,
      nightBrightness,
      dayBrightness,
      sunriseDuration,
      sunsetDuration,
    );
    const rgb = `rgb(${rgbw[0] || 0}, ${rgbw[1] || 0}, ${rgbw[2] || 0})`;
    const whiteAlpha = Math.max(0.08, Math.min(0.85, (rgbw[3] || 0) / 255));
    const priceEntity = this.config.price_entity || attr.price_entity || "";
    const batteryEntity = this.config.battery_entity || attr.battery_soc_entity || "";
    const timeLapseDurationEntity = this.config.time_lapse_duration_number || "";
    const timeLapseDuration = Number(
      this._hass.states[timeLapseDurationEntity]?.state
      ?? attr.time_lapse_duration_minutes
      ?? 1,
    );

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
            <span>Sonnenaufgang ${this.escape(sunrise)} · Rot → Weiss ${sunriseDuration} Min.</span>
            <span>Weiss → Rot ab ${this.escape(attr.sunset_phase_start || sunset)} · Untergang ${this.escape(sunset)}</span>
          </div>

          <div class="alc-grid">
            ${this.metric("Basis", `${base}%`)}
            ${this.metric("Weiss", `${white}%`)}
            ${this.metric("Preis", this.formatPrice(attr.price, this._hass.states[priceEntity]?.attributes?.unit_of_measurement))}
            ${this.metric("Preis-Dimmung", this.formatPercent(attr.price_dimming_pct))}
            ${this.metric("Speicher", this.formatPercent(attr.battery_soc))}
            ${this.metric("Preisregel", attr.price_ignored ? "Ignoriert" : "Aktiv")}
            ${this.metric("Solar", this.formatPower(attr.solar_power))}
            ${this.metric("Sonne regional", attr.regional_sun ? "Ja" : "Nein")}
            ${this.metric("Wolken", `${attr.cloudiness_pct ?? "-"}%`)}
          </div>

          ${this.timelineSection(attr, priceEntity, batteryEntity)}

          <div class="alc-controls">
            ${this.controlButton("simulation_switch", "Simulation ein", "turn_on")}
            ${this.controlButton("time_lapse_switch", "Zeitraffer starten", "turn_on")}
            ${this.controlButton("time_lapse_switch", "Zeitraffer stoppen", "turn_off")}
            ${this.timeLapseDurationControl(timeLapseDurationEntity, timeLapseDuration)}
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

    this.querySelectorAll("[data-time-lapse-duration]").forEach((input) => {
      input.addEventListener("change", () => {
        this._hass.callService("number", "set_value", {
          entity_id: input.dataset.timeLapseDuration,
          value: Number(input.value),
        });
      });
    });

    this.ensureTimelineData(priceEntity, batteryEntity);
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
        .alc-duration { background: var(--secondary-background-color); border-radius: 8px; flex: 1 1 220px; min-width: 0; padding: 9px 11px; }
        .alc-duration-head { align-items: center; display: flex; font-size: 12px; gap: 12px; justify-content: space-between; }
        .alc-duration-head strong { color: var(--primary-text-color); white-space: nowrap; }
        .alc-duration input { accent-color: var(--primary-color); cursor: pointer; margin: 8px 0 0; width: 100%; }
        .alc-timeline-section { border-top: 1px solid var(--divider-color); margin-top: 20px; padding-top: 18px; }
        .alc-timeline-title { font-size: 16px; font-weight: 650; }
        .alc-timeline-sub { color: var(--secondary-text-color); font-size: 12px; margin-top: 3px; }
        .alc-timeline-grid { display: grid; gap: 12px; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 12px; }
        .alc-timeline-card { background: color-mix(in srgb, var(--secondary-background-color) 84%, transparent); border: 1px solid color-mix(in srgb, var(--divider-color) 75%, transparent); border-radius: 12px; min-width: 0; overflow: hidden; padding: 13px; }
        .alc-timeline-head { align-items: flex-start; display: flex; gap: 12px; justify-content: space-between; }
        .alc-timeline-name { font-size: 14px; font-weight: 650; }
        .alc-timeline-range { color: var(--secondary-text-color); font-size: 11px; margin-top: 2px; }
        .alc-timeline-value { background: color-mix(in srgb, var(--primary-color) 20%, transparent); border-radius: 999px; color: var(--primary-text-color); flex: 0 0 auto; font-size: 12px; font-weight: 700; padding: 5px 8px; }
        .alc-timeline-chart { display: block; height: 166px; margin-top: 8px; overflow: visible; width: 100%; }
        .alc-timeline-chart text { fill: var(--secondary-text-color); font-family: var(--paper-font-body1_-_font-family, sans-serif); font-size: 16px; }
        .alc-chart-gridline { stroke: var(--divider-color); stroke-width: 1; }
        .alc-chart-axis { stroke: color-mix(in srgb, var(--secondary-text-color) 45%, transparent); stroke-width: 1; }
        .alc-chart-price-history { fill: none; stroke: #ffb454; stroke-linecap: round; stroke-linejoin: round; stroke-width: 4; }
        .alc-chart-price-forecast { fill: none; stroke: #57d9ff; stroke-dasharray: 8 6; stroke-linecap: round; stroke-linejoin: round; stroke-width: 4; }
        .alc-chart-battery { fill: none; stroke: #58e0a3; stroke-linecap: round; stroke-linejoin: round; stroke-width: 4; }
        .alc-chart-area-price { fill: #ffb454; opacity: 0.10; }
        .alc-chart-area-battery { fill: #58e0a3; opacity: 0.12; }
        .alc-chart-now-line { stroke: #ffffff; stroke-dasharray: 3 5; stroke-opacity: 0.72; stroke-width: 2; }
        .alc-chart-average { stroke: #ffcf67; stroke-dasharray: 10 6; stroke-opacity: 0.85; stroke-width: 2; }
        .alc-chart-threshold { stroke: #ff8a80; stroke-dasharray: 10 6; stroke-opacity: 0.9; stroke-width: 2; }
        .alc-chart-dot-price { fill: #ffb454; stroke: var(--card-background-color); stroke-width: 3; }
        .alc-chart-dot-battery { fill: #58e0a3; stroke: var(--card-background-color); stroke-width: 3; }
        .alc-legend { align-items: center; color: var(--secondary-text-color); display: flex; flex-wrap: wrap; font-size: 10px; gap: 10px; margin-top: 3px; }
        .alc-legend-item { align-items: center; display: inline-flex; gap: 5px; }
        .alc-legend-swatch { border-radius: 999px; display: inline-block; height: 3px; width: 18px; }
        .alc-legend-history { background: #ffb454; }
        .alc-legend-forecast { background: repeating-linear-gradient(90deg, #57d9ff 0 6px, transparent 6px 9px); }
        .alc-legend-battery { background: #58e0a3; }
        .alc-legend-threshold { background: repeating-linear-gradient(90deg, #ff8a80 0 6px, transparent 6px 9px); }
        .alc-timeline-stats { display: grid; gap: 6px; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-top: 10px; }
        .alc-timeline-stat { background: color-mix(in srgb, var(--primary-background-color) 62%, transparent); border-radius: 7px; min-width: 0; padding: 7px; }
        .alc-timeline-stat-label { color: var(--secondary-text-color); font-size: 9px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .alc-timeline-stat-value { font-size: 12px; font-weight: 650; margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .alc-timeline-placeholder { align-items: center; color: var(--secondary-text-color); display: flex; font-size: 12px; height: 166px; justify-content: center; text-align: center; }
        .alc-timeline-error { color: var(--warning-color, #ffb74d); font-size: 11px; margin-top: 9px; }
        @media (max-width: 520px) {
          .alc-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
          .alc-times { flex-direction: column; gap: 2px; }
          .alc-controls button { flex: 1 1 100%; justify-content: center; }
          .alc-timeline-grid { grid-template-columns: 1fr; }
          .alc-timeline-chart { height: 154px; }
        }
        @media (min-width: 521px) and (max-width: 900px) {
          .alc-timeline-grid { grid-template-columns: 1fr; }
        }
      </style>
    `;
  }

  timelineSection(attr, priceEntity, batteryEntity) {
    if (!priceEntity && !batteryEntity) {
      return "";
    }

    const error = this._timeline?.error
      ? `<div class="alc-timeline-error">${this.escape(this._timeline.error)}</div>`
      : "";

    return `
      <section class="alc-timeline-section">
        <div class="alc-timeline-title">Energie & Preis</div>
        <div class="alc-timeline-sub">Echte Home-Assistant-Historie und Tibber-Preise, ohne geschätzte Batteriewerte.</div>
        <div class="alc-timeline-grid">
          ${this.priceTimeline(attr, priceEntity)}
          ${this.batteryTimeline(attr, batteryEntity)}
        </div>
        ${error}
      </section>
    `;
  }

  priceTimeline(attr, priceEntity) {
    const priceState = priceEntity ? this._hass.states[priceEntity] : null;
    const unit = priceState?.attributes?.unit_of_measurement || "EUR/kWh";
    const current = this.numberOrNull(attr.price ?? priceState?.state);
    const history = this._timeline?.priceHistory || [];
    const forecast = this._timeline?.priceForecast || [];

    if (this._timeline?.loading && history.length === 0 && forecast.length === 0) {
      return this.timelinePlaceholder("Strompreis", "Verlauf und Tibber-Vorschau werden geladen …", current, unit);
    }

    if (history.length === 0 && forecast.length === 0) {
      return this.timelinePlaceholder("Strompreis", "Noch keine Preisdaten verfügbar", current, unit);
    }

    const now = Date.now();
    const start = now - (12 * 60 * 60 * 1000);
    const end = now + (24 * 60 * 60 * 1000);
    const past = history.filter((point) => point.time >= start && point.time <= now);
    const future = forecast.filter((point) => point.time >= now - (30 * 60 * 1000) && point.time <= end);
    const all = [...past, ...future];
    const values = all.map((point) => point.value).filter(Number.isFinite);
    const average = this.numberOrNull(attr.price_reference ?? priceState?.attributes?.avg_price);
    if (average !== null) {
      values.push(average);
    }

    const rawMin = Math.min(...values);
    const rawMax = Math.max(...values);
    const spread = Math.max(0.01, rawMax - rawMin);
    const min = Math.max(0, rawMin - (spread * 0.12));
    const max = rawMax + (spread * 0.12);
    const chart = this.chartGeometry(start, end, min, max);
    const pastPath = this.pointPath(past, chart);
    const futurePoints = past.length > 0 ? [past[past.length - 1], ...future] : future;
    const futurePath = this.pointPath(futurePoints, chart);
    const pastArea = this.areaPath(past, chart);
    const nowX = chart.x(now);
    const averageY = average === null ? null : chart.y(average);
    const lastPast = past[past.length - 1];
    const futureOnly = future.filter((point) => point.time >= now);
    const futureValues = futureOnly.map((point) => point.value);
    const forecastMin = futureValues.length ? Math.min(...futureValues) : null;
    const forecastMax = futureValues.length ? Math.max(...futureValues) : null;

    return `
      <div class="alc-timeline-card">
        <div class="alc-timeline-head">
          <div>
            <div class="alc-timeline-name">Strompreis</div>
            <div class="alc-timeline-range">12 h Rückblick · bis 24 h Tibber-Vorschau</div>
          </div>
          <div class="alc-timeline-value">${this.escape(this.formatPrice(current, unit))}</div>
        </div>
        <svg class="alc-timeline-chart" viewBox="0 0 640 210" role="img" aria-label="Strompreis-Rückblick und Vorschau">
          ${this.chartGrid(chart, min, max, (value) => this.formatPriceCompact(value, unit))}
          ${pastArea ? `<path d="${pastArea}" class="alc-chart-area-price"></path>` : ""}
          ${pastPath ? `<path d="${pastPath}" class="alc-chart-price-history"></path>` : ""}
          ${futurePath ? `<path d="${futurePath}" class="alc-chart-price-forecast"></path>` : ""}
          ${averageY === null ? "" : `<line x1="${chart.left}" y1="${averageY.toFixed(1)}" x2="${chart.rightEdge}" y2="${averageY.toFixed(1)}" class="alc-chart-average"></line>`}
          <line x1="${nowX.toFixed(1)}" y1="${chart.top}" x2="${nowX.toFixed(1)}" y2="${chart.bottomEdge}" class="alc-chart-now-line"></line>
          ${lastPast ? `<circle cx="${chart.x(lastPast.time).toFixed(1)}" cy="${chart.y(lastPast.value).toFixed(1)}" r="6" class="alc-chart-dot-price"></circle>` : ""}
          ${this.chartTimeLabels(chart, [
            [start, "−12 h"],
            [now, "Jetzt"],
            [now + (12 * 60 * 60 * 1000), "+12 h"],
            [end, "+24 h"],
          ])}
        </svg>
        <div class="alc-legend">
          <span class="alc-legend-item"><span class="alc-legend-swatch alc-legend-history"></span>Rückblick</span>
          <span class="alc-legend-item"><span class="alc-legend-swatch alc-legend-forecast"></span>Vorschau</span>
          <span class="alc-legend-item"><span class="alc-legend-swatch alc-legend-history"></span>Tagesmittel ${this.escape(this.formatPrice(average, unit))}</span>
        </div>
        <div class="alc-timeline-stats">
          ${this.timelineStat("Prognose min.", this.formatPrice(forecastMin, unit))}
          ${this.timelineStat("Prognose max.", this.formatPrice(forecastMax, unit))}
          ${this.timelineStat("Werte", futureOnly.length ? `${futureOnly.length} × 15 min` : "ausstehend")}
        </div>
      </div>
    `;
  }

  batteryTimeline(attr, batteryEntity) {
    const current = this.numberOrNull(attr.battery_soc ?? this._hass.states[batteryEntity]?.state);
    const threshold = this.numberOrNull(attr.battery_full_threshold) ?? 95;
    const history = this._timeline?.batteryHistory || [];

    if (this._timeline?.loading && history.length === 0) {
      return this.timelinePlaceholder("Batterieverlauf", "24-Stunden-Rückblick wird geladen …", current, "%");
    }

    if (history.length === 0) {
      return this.timelinePlaceholder("Batterieverlauf", "Noch keine Batteriehistorie verfügbar", current, "%");
    }

    const now = Date.now();
    const start = now - (24 * 60 * 60 * 1000);
    const points = history.filter((point) => point.time >= start && point.time <= now);
    const chart = this.chartGeometry(start, now, 0, 100);
    const line = this.pointPath(points, chart);
    const area = this.areaPath(points, chart);
    const thresholdY = chart.y(threshold);
    const last = points[points.length - 1];
    const values = points.map((point) => point.value);
    const minimum = values.length ? Math.min(...values) : null;
    const maximum = values.length ? Math.max(...values) : null;
    const trend = points.length > 1 ? points[points.length - 1].value - points[0].value : null;

    return `
      <div class="alc-timeline-card">
        <div class="alc-timeline-head">
          <div>
            <div class="alc-timeline-name">Batterieverlauf</div>
            <div class="alc-timeline-range">24 h Rückblick · voll ab ${Math.round(threshold)} %</div>
          </div>
          <div class="alc-timeline-value">${this.escape(this.formatPercent(current))}</div>
        </div>
        <svg class="alc-timeline-chart" viewBox="0 0 640 210" role="img" aria-label="Batterie-Ladezustand der letzten 24 Stunden">
          ${this.chartGrid(chart, 0, 100, (value) => `${Math.round(value)} %`)}
          ${area ? `<path d="${area}" class="alc-chart-area-battery"></path>` : ""}
          ${line ? `<path d="${line}" class="alc-chart-battery"></path>` : ""}
          <line x1="${chart.left}" y1="${thresholdY.toFixed(1)}" x2="${chart.rightEdge}" y2="${thresholdY.toFixed(1)}" class="alc-chart-threshold"></line>
          ${last ? `<circle cx="${chart.x(last.time).toFixed(1)}" cy="${chart.y(last.value).toFixed(1)}" r="6" class="alc-chart-dot-battery"></circle>` : ""}
          ${this.chartTimeLabels(chart, [
            [start, "−24 h"],
            [now - (12 * 60 * 60 * 1000), "−12 h"],
            [now, "Jetzt"],
          ])}
        </svg>
        <div class="alc-legend">
          <span class="alc-legend-item"><span class="alc-legend-swatch alc-legend-battery"></span>Growatt SOC</span>
          <span class="alc-legend-item"><span class="alc-legend-swatch alc-legend-threshold"></span>Vollgrenze ${Math.round(threshold)} %</span>
        </div>
        <div class="alc-timeline-stats">
          ${this.timelineStat("Minimum", this.formatPercent(minimum))}
          ${this.timelineStat("Maximum", this.formatPercent(maximum))}
          ${this.timelineStat("24-h-Änderung", trend === null ? "-" : `${trend >= 0 ? "+" : ""}${Math.round(trend)} %`)}
        </div>
      </div>
    `;
  }

  timelinePlaceholder(title, message, current, unit) {
    const value = unit === "%" ? this.formatPercent(current) : this.formatPrice(current, unit);
    return `
      <div class="alc-timeline-card">
        <div class="alc-timeline-head">
          <div>
            <div class="alc-timeline-name">${this.escape(title)}</div>
            <div class="alc-timeline-range">Rückblick und Vorschau</div>
          </div>
          <div class="alc-timeline-value">${this.escape(value)}</div>
        </div>
        <div class="alc-timeline-placeholder">${this.escape(message)}</div>
      </div>
    `;
  }

  timelineStat(label, value) {
    return `
      <div class="alc-timeline-stat">
        <div class="alc-timeline-stat-label">${this.escape(label)}</div>
        <div class="alc-timeline-stat-value">${this.escape(value)}</div>
      </div>
    `;
  }

  chartGeometry(start, end, min, max) {
    const left = 54;
    const rightEdge = 626;
    const top = 14;
    const bottomEdge = 170;
    return {
      bottomEdge,
      end,
      left,
      max,
      min,
      rightEdge,
      start,
      top,
      x: (time) => left + (((time - start) / Math.max(1, end - start)) * (rightEdge - left)),
      y: (value) => bottomEdge - (((value - min) / Math.max(0.000001, max - min)) * (bottomEdge - top)),
    };
  }

  chartGrid(chart, min, max, formatter) {
    const middle = min + ((max - min) / 2);
    return [max, middle, min].map((value) => {
      const y = chart.y(value).toFixed(1);
      return `
        <line x1="${chart.left}" y1="${y}" x2="${chart.rightEdge}" y2="${y}" class="alc-chart-gridline"></line>
        <text x="4" y="${Number(y) + 5}">${this.escape(formatter(value))}</text>
      `;
    }).join("");
  }

  chartTimeLabels(chart, labels) {
    return labels.map(([time, label], index) => {
      const x = chart.x(time);
      const anchor = index === 0 ? "start" : (index === labels.length - 1 ? "end" : "middle");
      return `<text x="${x.toFixed(1)}" y="202" text-anchor="${anchor}">${this.escape(label)}</text>`;
    }).join("");
  }

  pointPath(points, chart) {
    return points.map((point, index) => {
      const x = chart.x(point.time).toFixed(1);
      const y = chart.y(point.value).toFixed(1);
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    }).join(" ");
  }

  areaPath(points, chart) {
    if (points.length < 2) {
      return "";
    }
    const line = this.pointPath(points, chart);
    const firstX = chart.x(points[0].time).toFixed(1);
    const lastX = chart.x(points[points.length - 1].time).toFixed(1);
    return `${line} L ${lastX} ${chart.bottomEdge} L ${firstX} ${chart.bottomEdge} Z`;
  }

  ensureTimelineData(priceEntity, batteryEntity) {
    if (!this._hass || (!priceEntity && !batteryEntity)) {
      return;
    }

    const key = `${priceEntity}|${batteryEntity}`;
    const fresh = this._timeline?.key === key && (Date.now() - this._timeline.loadedAt) < (5 * 60 * 1000);
    if (this._timeline?.loading || fresh) {
      return;
    }

    this._timeline = { ...this._timeline, error: "", key, loading: true };
    this.loadTimelineData(priceEntity, batteryEntity)
      .then((data) => {
        this._timeline = {
          ...data,
          error: "",
          key,
          loadedAt: Date.now(),
          loading: false,
        };
        this.render();
      })
      .catch((error) => {
        this._timeline = {
          ...this._timeline,
          error: `Verlaufsdaten konnten nicht geladen werden: ${error?.message || error}`,
          key,
          loadedAt: Date.now(),
          loading: false,
        };
        this.render();
      });
  }

  async loadTimelineData(priceEntity, batteryEntity) {
    const now = new Date();
    const historyStart = new Date(now.getTime() - (24 * 60 * 60 * 1000));
    const entityIds = [priceEntity, batteryEntity].filter(Boolean);
    const historyResult = entityIds.length
      ? await this._hass.callWS({
          type: "history/history_during_period",
          start_time: historyStart.toISOString(),
          end_time: now.toISOString(),
          entity_ids: entityIds,
          include_start_time_state: true,
          minimal_response: true,
          no_attributes: true,
          significant_changes_only: true,
        })
      : [];

    const priceHistory = priceEntity
      ? this.historySeries(historyResult, priceEntity, entityIds.indexOf(priceEntity))
      : [];
    const batteryHistory = batteryEntity
      ? this.historySeries(historyResult, batteryEntity, entityIds.indexOf(batteryEntity))
      : [];
    let priceForecast = [];

    if (priceEntity) {
      try {
        priceForecast = await this.fetchTibberPrices(priceEntity, now);
      } catch (_error) {
        priceForecast = [];
      }
    }

    return { batteryHistory, priceForecast, priceHistory };
  }

  historySeries(result, entityId, fallbackIndex) {
    let items = [];
    if (Array.isArray(result)) {
      if (result.length > 0 && Array.isArray(result[0])) {
        items = result.find((series) => series.some((item) => item?.entity_id === entityId))
          || result[fallbackIndex]
          || [];
      } else {
        items = result.filter((item) => !item?.entity_id || item.entity_id === entityId);
      }
    } else if (result && typeof result === "object") {
      items = result[entityId] || result.states?.[entityId] || [];
    }

    let previousState = null;
    return items.map((item) => {
      const rawState = item?.state ?? item?.s ?? previousState;
      if (rawState !== undefined && rawState !== null) {
        previousState = rawState;
      }
      const rawTime = item?.last_updated ?? item?.last_changed ?? item?.lu ?? item?.lc;
      const time = typeof rawTime === "number"
        ? (rawTime > 1000000000000 ? rawTime : rawTime * 1000)
        : Date.parse(rawTime);
      const value = this.numberOrNull(rawState);
      return { time, value };
    }).filter((point) => Number.isFinite(point.time) && point.value !== null);
  }

  async fetchTibberPrices(priceEntity, now) {
    const start = new Date(now);
    start.setHours(0, 0, 0, 0);
    const end = new Date(start);
    end.setDate(end.getDate() + 1);
    end.setHours(23, 59, 59, 0);

    const result = await this._hass.callWS({
      type: "call_service",
      domain: "tibber",
      service: "get_prices",
      service_data: {
        start: this.localDateTime(start),
        end: this.localDateTime(end),
      },
      return_response: true,
    });
    const response = result?.response || result?.service_response || result || {};
    const groups = response.prices || {};
    const nickname = this._hass.states[priceEntity]?.attributes?.app_nickname;
    const entries = (nickname && groups[nickname]) || Object.values(groups)[0] || [];

    return entries.map((item) => ({
      time: Date.parse(item.start_time),
      value: this.numberOrNull(item.price),
    })).filter((point) => Number.isFinite(point.time) && point.value !== null);
  }

  localDateTime(value) {
    const pad = (number) => String(number).padStart(2, "0");
    return `${value.getFullYear()}-${pad(value.getMonth() + 1)}-${pad(value.getDate())} ${pad(value.getHours())}:${pad(value.getMinutes())}:${pad(value.getSeconds())}`;
  }

  numberOrNull(value) {
    if (value === undefined || value === null || value === "" || value === "-") {
      return null;
    }
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  formatPrice(value, unit) {
    const number = this.numberOrNull(value);
    if (number === null) {
      return "-";
    }
    if (String(unit).toLowerCase().includes("eur/kwh")) {
      return `${(number * 100).toLocaleString("de-DE", { minimumFractionDigits: 1, maximumFractionDigits: 1 })} ct/kWh`;
    }
    return `${number.toLocaleString("de-DE", { maximumFractionDigits: 3 })} ${unit || ""}`.trim();
  }

  formatPriceCompact(value, unit) {
    const number = this.numberOrNull(value);
    if (number === null) {
      return "-";
    }
    if (String(unit).toLowerCase().includes("eur/kwh")) {
      return `${(number * 100).toFixed(1)} ct`;
    }
    return number.toFixed(3);
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

  timeLapseDurationControl(entity, value) {
    if (!entity) {
      return "";
    }
    const duration = Math.max(1, Math.min(10, Math.round(Number(value) || 1)));
    return `
      <label class="alc-duration">
        <span class="alc-duration-head">
          <span>24-Stunden-Dauer</span>
          <strong>${duration} Min.</strong>
        </span>
        <input
          type="range"
          min="1"
          max="10"
          step="1"
          value="${duration}"
          data-time-lapse-duration="${this.escape(entity)}"
          aria-label="Dauer des 24-Stunden-Zeitraffers in Minuten"
        />
      </label>
    `;
  }

  buildCurve(sunrise, sunset, nightPct, dayPct, sunriseDuration, sunsetDuration) {
    const sunriseMinute = this.parseMinute(sunrise, 360);
    const sunsetMinute = this.parseMinute(sunset, 1080);
    const points = [];

    for (let index = 0; index <= 96; index += 1) {
      const minute = index * 15;
      const pct = this.profileAt(
        minute,
        sunriseMinute,
        sunsetMinute,
        nightPct,
        dayPct,
        sunriseDuration,
        sunsetDuration,
      );
      const x = (index / 96) * 320;
      const y = 88 - (pct / 100) * 72;
      points.push([x, y]);
    }

    const line = points.map((point, index) => `${index === 0 ? "M" : "L"} ${point[0].toFixed(1)} ${point[1].toFixed(1)}`).join(" ");
    const fill = `${line} L 320 92 L 0 92 Z`;
    return { line, fill };
  }

  profileAt(minute, sunrise, sunset, night, day, sunriseDuration = 60, sunsetDuration = 90) {
    const sunsetStart = sunset - sunsetDuration;
    if (minute >= sunrise && minute < sunrise + sunriseDuration) {
      return night + ((day - night) * ((minute - sunrise) / sunriseDuration));
    }
    if (minute >= sunrise + sunriseDuration && minute < sunsetStart) {
      return day;
    }
    if (minute >= sunsetStart && minute < sunset) {
      return day + ((night - day) * ((minute - sunsetStart) / sunsetDuration));
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
      night: "Mondlicht",
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
