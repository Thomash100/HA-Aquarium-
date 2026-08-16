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
    const rgbw = Array.isArray(attr.rgbw) ? attr.rgbw : [0, 10, 90, 0];
    const target = Number(attr.target_pct || 0);
    const base = Number(attr.base_pct || target || 0);
    const white = Number(attr.white_pct || 0);
    const currentTime = attr.time || "--:--";
    const sunrise = attr.sunrise || "06:00";
    const sunriseActual = attr.sunrise_actual || sunrise;
    const sunset = attr.sunset || "18:00";
    const sunriseDuration = Number(attr.sunrise_duration_minutes ?? 60);
    const sunsetDuration = Number(attr.sunset_duration_minutes ?? 90);
    const sunriseStartRgbw = this.normalizeRgbw(attr.sunrise_start_rgbw || attr.sunrise_rgbw, [255, 0, 0, 0]);
    const sunriseEndRgbw = this.normalizeRgbw(attr.sunrise_end_rgbw, [190, 220, 255, 255]);
    const sunsetStartRgbw = this.normalizeRgbw(attr.sunset_start_rgbw, [190, 220, 255, 255]);
    const sunsetEndRgbw = this.normalizeRgbw(attr.sunset_end_rgbw || attr.sunset_rgbw, [255, 0, 0, 0]);
    const celestial = this.celestialGeometry(currentTime, sunrise, sunset);
    const moonPhaseIcon = attr.moon_phase_icon || "🌙";
    const moonPhaseLabel = attr.moon_phase_label || "Mondphase";
    const moonPhaseBrightness = Number(attr.moon_phase_brightness_pct ?? 60);
    const moonCloudDimming = Number(attr.moon_cloud_dimming_pct ?? 0);
    const dayBrightness = Number(attr.day_brightness_pct ?? Math.max(base, target, 70));
    const nightBrightness = Number(attr.night_brightness_pct ?? 3);
    const rgb = `rgb(${rgbw[0] || 0}, ${rgbw[1] || 0}, ${rgbw[2] || 0})`;
    const whiteAlpha = Math.max(0.08, Math.min(0.85, (rgbw[3] || 0) / 255));
    const priceEntity = this.config.price_entity || attr.price_entity || "";
    const batteryEntity = this.config.battery_entity || attr.battery_soc_entity || "";
    const timeLapseDurationEntity = this.config.time_lapse_duration_number || "";
    const sunriseOffsetEntity = this.config.sunrise_offset_number || "";
    const sunriseDurationEntity = this.config.sunrise_duration_number || "";
    const sunsetDurationEntity = this.config.sunset_duration_number || "";
    const aquariumPreviewEntity = this.config.aquarium_preview_switch || "";
    const aquariumPreviewActive = (
      this._hass.states[aquariumPreviewEntity]?.state === "on"
      || Boolean(attr.aquarium_preview)
    );
    const timeLapseDuration = Number(
      this._hass.states[timeLapseDurationEntity]?.state
      ?? attr.time_lapse_duration_minutes
      ?? 1,
    );
    const sunriseOffsetHours = Number(
      this._hass.states[sunriseOffsetEntity]?.state
      ?? attr.sunrise_offset_hours
      ?? 0,
    );
    const configuredSunriseDuration = Number(
      this._hass.states[sunriseDurationEntity]?.state
      ?? sunriseDuration,
    );
    const configuredSunsetDuration = Number(
      this._hass.states[sunsetDurationEntity]?.state
      ?? sunsetDuration,
    );
    const sunriseCss = this.rgbwCss(sunriseStartRgbw);
    const sunsetCss = this.rgbwCss(sunsetEndRgbw);

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

          <div class="alc-celestial" style="--alc-rgb: ${rgb}; --alc-white: ${whiteAlpha}; --alc-sunrise: ${sunriseCss}; --alc-sunset: ${sunsetCss};">
            <svg class="alc-sky" viewBox="0 0 720 190" role="img" aria-label="Sonnenbahn und Mondphase ueber 24 Stunden">
              <path d="${celestial.sunArc}" class="alc-sun-arc"></path>
              <path d="${celestial.moonEveningArc}" class="alc-moon-arc"></path>
              <path d="${celestial.moonMorningArc}" class="alc-moon-arc"></path>
              <line x1="0" y1="138" x2="720" y2="138" class="alc-horizon-line"></line>
              <line x1="${celestial.nowX}" y1="12" x2="${celestial.nowX}" y2="166" class="alc-sky-now"></line>
              ${celestial.isDay
                ? `<circle cx="${celestial.bodyX}" cy="${celestial.bodyY}" r="14" class="alc-sun-body"></circle>`
                : `<text x="${celestial.bodyX}" y="${celestial.bodyY + 9}" class="alc-moon-body" text-anchor="middle">${this.escape(moonPhaseIcon)}</text>`}
              <text x="${celestial.sunriseX}" y="160" class="alc-sky-label" text-anchor="middle">${this.escape(sunrise)}</text>
              <text x="${celestial.sunsetX}" y="160" class="alc-sky-label" text-anchor="middle">${this.escape(sunset)}</text>
              <text x="360" y="181" class="alc-moon-label" text-anchor="middle">${this.escape(moonPhaseIcon)} ${this.escape(moonPhaseLabel)} · Mond ${Math.round(moonPhaseBrightness)}% · Wolken −${Math.round(moonCloudDimming)}%</text>
            </svg>
          </div>

          <div class="alc-times">
            <span>Reale Sonne ${this.escape(sunriseActual)} · Lichtstart ${this.escape(sunrise)} (${this.escape(this.formatSignedHours(sunriseOffsetHours))}) · Anfang → Ende ${configuredSunriseDuration} Min.</span>
            <span>Anfang → Ende ${configuredSunsetDuration} Min. · ab ${this.escape(attr.sunset_phase_start || sunset)} · Untergang ${this.escape(sunset)}</span>
          </div>

          ${this.intensitySection(
            attr,
            sunrise,
            sunset,
            nightBrightness,
            dayBrightness,
            configuredSunriseDuration,
            configuredSunsetDuration,
          )}

          ${this.sunriseOffsetControl(sunriseOffsetEntity, sunriseOffsetHours)}

          ${this.transitionColorControls(
            sunriseStartRgbw,
            sunriseEndRgbw,
            sunsetStartRgbw,
            sunsetEndRgbw,
            attr.config_entry_id || this.config.config_entry_id || "",
            sunriseDurationEntity,
            configuredSunriseDuration,
            sunsetDurationEntity,
            configuredSunsetDuration,
          )}

          <div class="alc-grid">
            ${this.metric("Basis", `${base}%`)}
            ${this.metric("Tagesmaximum", `${attr.midday_peak_time || "12:00"} · ${dayBrightness}%`)}
            ${this.metric("RGBW", rgbw.map((channel) => Math.round(Number(channel) || 0)).join(" / "))}
            ${this.metric("Weiss", `${white}%`)}
            ${this.metric("Preis", this.formatPrice(attr.price, this._hass.states[priceEntity]?.attributes?.unit_of_measurement))}
            ${this.metric("Preis-Dimmung", this.formatPercent(attr.price_dimming_pct))}
            ${this.metric("Speicher", this.formatPercent(attr.battery_soc))}
            ${this.metric("Preisregel", this.priceRuleLabel(attr))}
            ${this.metric("Solar", this.formatPower(attr.solar_power))}
            ${this.metric("Sonne regional", attr.regional_sun ? "Ja" : "Nein")}
            ${this.metric("Wolken", `${attr.cloudiness_pct ?? "-"}%`)}
            ${this.metric("Mondlicht", this.formatPercent(attr.moonlight_target_pct))}
            ${this.metric("Mondphase", `${Math.round(moonPhaseBrightness)}%`)}
            ${this.metric("Mond-Wolken", `−${Math.round(moonCloudDimming)}%`)}
            ${this.metric("Sonnenaufgang", `${sunrise} · ${this.formatSignedHours(sunriseOffsetHours)}`)}
            ${this.metric("Am Aquarium", aquariumPreviewActive ? "Vorschau aktiv" : "Geschuetzt")}
          </div>

          ${this.timelineSection(attr, priceEntity, batteryEntity)}

          <div class="alc-controls">
            ${this.controlButton("simulation_switch", "Simulation ein", "turn_on")}
            ${this.controlButton("time_lapse_switch", "Zeitraffer starten", "turn_on")}
            ${this.controlButton("time_lapse_switch", "Zeitraffer stoppen", "turn_off")}
            ${aquariumPreviewActive
              ? this.controlButton("aquarium_preview_switch", "Aquarium-Vorschau stoppen", "turn_off")
              : this.controlButton(
                "aquarium_preview_switch",
                "Am Aquarium zeigen",
                "turn_on",
                "Der komplette simulierte Tag wird jetzt einmal ueber die echten Aquarium-Leuchten abgespielt. Starten?",
              )}
            ${this.timeLapseDurationControl(timeLapseDurationEntity, timeLapseDuration)}
          </div>
          ${aquariumPreviewEntity ? `
            <div class="alc-preview-note">
              Bei eingeschalteter Steuerung bewegt die Aquarium-Vorschau echte Leuchten, endet nach einem Durchlauf und stellt den vorherigen Lichtzustand wieder her.
            </div>
          ` : ""}
        </div>
      </ha-card>
    `;

    this.querySelectorAll("[data-domain]").forEach((button) => {
      button.addEventListener("click", () => {
        if (button.dataset.confirm && !window.confirm(button.dataset.confirm)) {
          return;
        }
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

    this.querySelectorAll("[data-sunrise-offset]").forEach((input) => {
      input.addEventListener("change", () => {
        this._hass.callService("number", "set_value", {
          entity_id: input.dataset.sunriseOffset,
          value: Number(input.value),
        });
      });
    });

    this.querySelectorAll("[data-transition-duration]").forEach((input) => {
      input.addEventListener("change", () => {
        const value = Math.max(10, Math.min(240, Math.round(Number(input.value) / 5) * 5));
        input.value = String(value);
        this._hass.callService("number", "set_value", {
          entity_id: input.dataset.transitionDuration,
          value,
        });
      });
    });

    this.querySelectorAll("[data-duration-delta]").forEach((button) => {
      button.addEventListener("click", () => {
        const input = this.querySelector(`[data-transition-duration="${button.dataset.durationEntity}"]`);
        if (!input) {
          return;
        }
        input.value = String(Math.max(10, Math.min(240, Number(input.value) + Number(button.dataset.durationDelta))));
        input.dispatchEvent(new Event("change"));
      });
    });

    this.querySelectorAll("[data-rgbw-editor]").forEach((editor) => {
      editor.querySelectorAll("[data-rgbw-channel]").forEach((input) => {
        input.addEventListener("input", () => this.previewTransitionColor(editor));
        input.addEventListener("change", () => this.saveTransitionColor(editor));
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
        .alc-celestial { background: linear-gradient(90deg, #071022 0%, #15254d 17%, var(--alc-sunrise) 25%, #56b9e9 49%, var(--alc-sunset) 77%, #15254d 84%, #071022 100%); border-radius: 12px; box-shadow: inset 0 -34px 58px rgba(0,0,0,0.30); margin-top: 18px; overflow: hidden; position: relative; }
        .alc-celestial::after { background: radial-gradient(circle at 50% 38%, rgba(255,255,255,var(--alc-white)), transparent 34%); content: ""; inset: 0; pointer-events: none; position: absolute; }
        .alc-sky { display: block; height: auto; overflow: visible; position: relative; width: 100%; z-index: 1; }
        .alc-sun-arc { fill: none; stroke: rgba(255,221,119,0.78); stroke-dasharray: 7 6; stroke-linecap: round; stroke-width: 3; }
        .alc-moon-arc { fill: none; stroke: rgba(181,203,255,0.55); stroke-dasharray: 5 7; stroke-linecap: round; stroke-width: 2.5; }
        .alc-horizon-line { stroke: rgba(255,255,255,0.38); stroke-width: 2; }
        .alc-sky-now { stroke: rgba(255,255,255,0.72); stroke-dasharray: 3 5; stroke-width: 1.5; }
        .alc-sun-body { fill: #ffd75e; filter: drop-shadow(0 0 12px rgba(255,211,82,0.95)); }
        .alc-moon-body { dominant-baseline: central; font-family: "Segoe UI Emoji", "Apple Color Emoji", sans-serif; font-size: 32px; filter: drop-shadow(0 0 8px rgba(202,218,255,0.72)); }
        .alc-sky-label { fill: rgba(255,255,255,0.82); font-size: 11px; font-weight: 650; }
        .alc-moon-label { fill: rgba(230,237,255,0.88); font-family: var(--paper-font-body1_-_font-family, sans-serif); font-size: 11px; }
        .alc-times { color: var(--secondary-text-color); display: flex; font-size: 12px; justify-content: space-between; gap: 12px; margin-top: 4px; }
        .alc-effect { background: color-mix(in srgb, var(--secondary-background-color) 86%, transparent); border: 1px solid color-mix(in srgb, var(--divider-color) 76%, transparent); border-radius: 12px; margin-top: 16px; overflow: hidden; padding: 13px; }
        .alc-effect-head { align-items: flex-start; display: flex; gap: 12px; justify-content: space-between; }
        .alc-effect-title { font-size: 15px; font-weight: 700; }
        .alc-effect-sub { color: var(--secondary-text-color); font-size: 11px; line-height: 1.35; margin-top: 3px; }
        .alc-effect-current { background: color-mix(in srgb, var(--primary-color) 22%, transparent); border-radius: 999px; flex: 0 0 auto; font-size: 12px; font-weight: 700; padding: 6px 9px; }
        .alc-effect-chart { display: block; height: 205px; margin-top: 7px; overflow: visible; width: 100%; }
        .alc-effect-chart text { fill: var(--secondary-text-color); font-family: var(--paper-font-body1_-_font-family, sans-serif); font-size: 14px; }
        .alc-effect-area { fill: #26b7df; opacity: 0.13; }
        .alc-effect-base { fill: none; stroke: #86a6c7; stroke-dasharray: 8 6; stroke-linecap: round; stroke-linejoin: round; stroke-width: 3; }
        .alc-effect-result { fill: none; filter: drop-shadow(0 0 4px rgba(38,183,223,0.35)); stroke: #26b7df; stroke-linecap: round; stroke-linejoin: round; stroke-width: 5; }
        .alc-effect-price { fill: none; stroke: #ffad42; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5; }
        .alc-effect-cloud { fill: none; stroke: #a58dd7; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5; }
        .alc-effect-battery { fill: none; stroke: #48c98b; stroke-linecap: round; stroke-linejoin: round; stroke-width: 2.5; }
        .alc-effect-now { stroke: var(--primary-text-color); stroke-dasharray: 3 5; stroke-opacity: 0.72; stroke-width: 2; }
        .alc-effect-noon { stroke: #ffd45d; stroke-dasharray: 8 6; stroke-opacity: 0.65; stroke-width: 2; }
        .alc-effect-noon-dot { fill: #ffd45d; stroke: var(--card-background-color); stroke-width: 3; }
        .alc-effect-dot { fill: #26b7df; stroke: var(--card-background-color); stroke-width: 3; }
        .alc-effect-factors { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
        .alc-effect-pill { background: color-mix(in srgb, var(--primary-background-color) 65%, transparent); border-radius: 999px; color: var(--secondary-text-color); font-size: 10px; padding: 5px 8px; }
        .alc-legend-base { background: repeating-linear-gradient(90deg, #86a6c7 0 6px, transparent 6px 9px); }
        .alc-legend-result { background: #26b7df; }
        .alc-legend-price { background: #ffad42; }
        .alc-legend-cloud { background: #a58dd7; }
        .alc-color-grid { display: grid; gap: 12px; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 14px; }
        .alc-color-editor { background: var(--secondary-background-color); border: 1px solid color-mix(in srgb, var(--divider-color) 70%, transparent); border-radius: 12px; padding: 12px; }
        .alc-color-editor-title { font-size: 15px; font-weight: 700; }
        .alc-color-points { display: grid; gap: 10px; grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top: 12px; }
        .alc-color-point { background: color-mix(in srgb, var(--primary-background-color) 64%, transparent); border-radius: 10px; min-width: 0; padding: 10px; }
        .alc-color-main { align-items: center; display: flex; gap: 9px; }
        .alc-color-swatch { border: 2px solid rgba(255,255,255,0.48); border-radius: 50%; box-shadow: 0 0 0 1px rgba(0,0,0,0.25); flex: 0 0 auto; height: 36px; width: 36px; }
        .alc-color-copy { min-width: 0; }
        .alc-color-title { font-size: 13px; font-weight: 650; }
        .alc-color-values { color: var(--secondary-text-color); font-size: 10px; margin-top: 2px; }
        .alc-channel { align-items: center; display: grid; gap: 7px; grid-template-columns: 18px minmax(0, 1fr) 30px; margin-top: 9px; }
        .alc-channel-label { font-size: 12px; font-weight: 750; text-align: center; }
        .alc-channel-value { color: var(--secondary-text-color); font-variant-numeric: tabular-nums; font-size: 11px; text-align: right; }
        .alc-channel-slider { appearance: none; background: color-mix(in srgb, currentColor 18%, transparent); border-radius: 999px; cursor: pointer; height: 12px; margin: 0; touch-action: pan-y; width: 100%; }
        .alc-channel-slider::-webkit-slider-thumb { appearance: none; background: currentColor; border: 2px solid var(--card-background-color); border-radius: 50%; box-shadow: 0 1px 4px rgba(0,0,0,0.36); height: 28px; width: 28px; }
        .alc-channel-slider::-moz-range-thumb { background: currentColor; border: 2px solid var(--card-background-color); border-radius: 50%; box-shadow: 0 1px 4px rgba(0,0,0,0.36); height: 24px; width: 24px; }
        .alc-channel-r { color: #f44336; }
        .alc-channel-g { color: #43a047; }
        .alc-channel-b { color: #3f82ff; }
        .alc-channel-w { color: #d2d6db; }
        .alc-transition-duration { margin-top: 12px; }
        .alc-duration-stepper { align-items: center; display: grid; gap: 8px; grid-template-columns: 46px minmax(72px, 1fr) 46px; margin-top: 7px; }
        .alc-duration-stepper button { background: color-mix(in srgb, var(--primary-color) 18%, var(--card-background-color)); border: 1px solid color-mix(in srgb, var(--primary-color) 50%, transparent); border-radius: 9px; color: var(--primary-text-color); cursor: pointer; font: inherit; font-size: 22px; min-height: 44px; }
        .alc-duration-stepper input { background: var(--card-background-color); border: 1px solid var(--divider-color); border-radius: 9px; color: var(--primary-text-color); font: inherit; font-size: 16px; font-weight: 700; height: 42px; min-width: 0; text-align: center; width: 100%; }
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
        .alc-sunrise-offset { display: block; margin-top: 14px; }
        .alc-preview-note { color: var(--secondary-text-color); font-size: 11px; line-height: 1.4; margin-top: 8px; }
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
          .alc-color-grid { grid-template-columns: 1fr; }
          .alc-color-points { grid-template-columns: 1fr; }
          .alc-effect-chart { height: 184px; }
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

  intensitySection(attr, sunrise, sunset, nightPct, dayPct, sunriseDuration, sunsetDuration) {
    const projection = this.buildIntensityProjection(
      attr,
      sunrise,
      sunset,
      nightPct,
      dayPct,
      sunriseDuration,
      sunsetDuration,
    );
    const chart = projection.chart;
    const currentX = chart.x(projection.now);
    const currentTarget = Math.max(0, Math.min(100, Number(attr.target_pct) || 0));
    const currentY = chart.y(currentTarget);
    const cloudDimming = Math.round(
      (1 - ((Number(attr.weather_factor) || 1) * (Number(attr.cloud_factor) || 1))) * 100,
    );
    const batteryText = attr.battery_full
      ? `Akku ${this.formatPercent(attr.battery_soc)}: Preis ignoriert`
      : `Akku ${this.formatPercent(attr.battery_soc)}`;

    return `
      <section class="alc-effect">
        <div class="alc-effect-head">
          <div>
            <div class="alc-effect-title">Lichtintensität über den Tag</div>
            <div class="alc-effect-sub">Tagesbogen mit Sollmaximum um 12:00 Uhr; das Ergebnis reagiert deutlich auf Wolken, Strompreis und Growatt-Akku.</div>
          </div>
          <div class="alc-effect-current">Jetzt ${Math.round(currentTarget)} %</div>
        </div>
        <svg class="alc-effect-chart" viewBox="0 0 640 210" role="img" aria-label="Wirksame Lichtintensitaet mit Wolken-, Preis- und Batterieeinfluss">
          ${this.chartGrid(chart, 0, 100, (value) => `${Math.round(value)} %`)}
          <path d="${projection.resultArea}" class="alc-effect-area"></path>
          <path d="${projection.basePath}" class="alc-effect-base"></path>
          <path d="${projection.resultPath}" class="alc-effect-result"></path>
          <path d="${projection.pricePath}" class="alc-effect-price"></path>
          <path d="${projection.cloudPath}" class="alc-effect-cloud"></path>
          ${projection.batteryPath ? `<path d="${projection.batteryPath}" class="alc-effect-battery"></path>` : ""}
          <line x1="${projection.noonX.toFixed(1)}" y1="${chart.top}" x2="${projection.noonX.toFixed(1)}" y2="${chart.bottomEdge}" class="alc-effect-noon"></line>
          <circle cx="${projection.noonX.toFixed(1)}" cy="${projection.noonY.toFixed(1)}" r="5" class="alc-effect-noon-dot"></circle>
          <line x1="${currentX.toFixed(1)}" y1="${chart.top}" x2="${currentX.toFixed(1)}" y2="${chart.bottomEdge}" class="alc-effect-now"></line>
          <circle cx="${currentX.toFixed(1)}" cy="${currentY.toFixed(1)}" r="6" class="alc-effect-dot"></circle>
          ${this.chartTimeLabels(chart, [
            [projection.start, "00"],
            [projection.start + (6 * 60 * 60 * 1000), "06"],
            [projection.start + (12 * 60 * 60 * 1000), "12"],
            [projection.start + (18 * 60 * 60 * 1000), "18"],
            [projection.end, "24 Uhr"],
          ])}
        </svg>
        <div class="alc-legend">
          <span class="alc-legend-item"><span class="alc-legend-swatch alc-legend-base"></span>Grundprofil</span>
          <span class="alc-legend-item"><span class="alc-legend-swatch alc-legend-result"></span>Ergebnis</span>
          <span class="alc-legend-item"><span class="alc-legend-swatch alc-legend-price"></span>Preisfaktor</span>
          <span class="alc-legend-item"><span class="alc-legend-swatch alc-legend-cloud"></span>Wolkenfaktor</span>
          ${projection.batteryPath ? `<span class="alc-legend-item"><span class="alc-legend-swatch alc-legend-battery"></span>Akku-SOC</span>` : ""}
        </div>
        <div class="alc-effect-factors">
          <span class="alc-effect-pill">Wolken aktuell −${Math.max(0, cloudDimming)} % · wirksam ${Math.round(Number(attr.effective_cloudiness_pct) || 0)} %</span>
          <span class="alc-effect-pill">Preis aktuell −${Math.round(Number(attr.price_dimming_pct) || 0)} %</span>
          <span class="alc-effect-pill">${this.escape(batteryText)}</span>
          <span class="alc-effect-pill">Zukunft: Preisprognose · Akku-SOC gehalten · Wolken aktuell</span>
        </div>
      </section>
    `;
  }

  buildIntensityProjection(attr, sunrise, sunset, nightPct, dayPct, sunriseDuration, sunsetDuration) {
    const startDate = new Date();
    startDate.setHours(0, 0, 0, 0);
    const start = startDate.getTime();
    const end = start + (24 * 60 * 60 * 1000);
    const realNow = new Date();
    const fallbackMinute = (realNow.getHours() * 60) + realNow.getMinutes();
    const displayMinute = this.parseMinute(attr.time, fallbackMinute);
    const now = start + (displayMinute * 60 * 1000);
    const chart = this.chartGeometry(start, end, 0, 100);
    const sunriseMinute = this.parseMinute(sunrise, 360);
    const sunsetMinute = this.parseMinute(sunset, 1080);
    const pricePoints = [
      ...(this._timeline?.priceHistory || []),
      ...(this._timeline?.priceForecast || []),
    ].sort((left, right) => left.time - right.time);
    const batteryPoints = [...(this._timeline?.batteryHistory || [])]
      .sort((left, right) => left.time - right.time);
    const currentPrice = this.numberOrNull(attr.price);
    const currentBattery = this.numberOrNull(attr.battery_soc);
    const reference = this.numberOrNull(attr.price_reference);
    const ceiling = this.numberOrNull(attr.price_ceiling);
    const maxDimming = Math.max(0, Math.min(100, Number(attr.price_dimming_max_pct) || 0)) / 100;
    const priceResponseExponent = Math.max(0.1, Math.min(1, Number(attr.price_response_exponent) || 0.65));
    const batteryThreshold = this.numberOrNull(attr.battery_full_threshold) ?? 95;
    const cloudiness = Math.max(0, Math.min(1, (Number(attr.cloudiness_pct) || 0) / 100));
    const cloudStrength = Math.max(0, Math.min(1, (Number(attr.cloud_strength_pct) || 0) / 100));
    const cloudSimulationCoverage = Math.max(0, Math.min(1, Number(attr.cloud_simulation_coverage) || 0.25));
    const cloudWeatherWeight = Math.max(0, Math.min(1, Number(attr.cloud_weather_weight) || 0.30));
    const cloudWaveStrength = Math.max(0, Math.min(1, Number(attr.cloud_wave_strength) || 0.60));
    const dayEdgeFactor = Math.max(0.1, Math.min(1, Number(attr.day_edge_brightness_factor) || 0.55));
    const middayPeakMinute = Math.max(0, Math.min(1439, Number(attr.midday_peak_minute) || 720));
    const moonPhaseFactor = Math.max(0, Math.min(1, Number(attr.moon_phase_factor) || 0.6));
    const basePoints = [];
    const resultPoints = [];
    const priceFactorPoints = [];
    const cloudFactorPoints = [];
    const batterySocPoints = [];

    for (let minute = 0; minute <= 1440; minute += 15) {
      const time = start + (minute * 60 * 1000);
      const wrappedMinute = minute === 1440 ? 1439 : minute;
      const base = this.profileAt(
        wrappedMinute,
        sunriseMinute,
        sunsetMinute,
        nightPct,
        dayPct,
        sunriseDuration,
        sunsetDuration,
        dayEdgeFactor,
        middayPeakMinute,
      );
      const night = wrappedMinute < sunriseMinute || wrappedMinute >= sunsetMinute;
      const wave = (Math.sin((wrappedMinute / 1440) * Math.PI * 2 * 8) + 1) / 2;
      const battery = this.timelineValueAt(batteryPoints, time, currentBattery);
      const price = this.timelineValueAt(pricePoints, time, currentPrice);
      const batteryFull = battery !== null && battery >= batteryThreshold;
      const priceFactor = night || batteryFull
        ? 1
        : this.priceFactorAt(
            price,
            reference,
            ceiling,
            maxDimming,
            priceResponseExponent,
            attr.price_factor,
          );
      let cloudFactor;
      let result;
      if (night) {
        cloudFactor = Math.max(
          0.35,
          Math.min(1, 1 - (cloudiness * cloudStrength * (0.25 + (0.75 * wave)) * 0.55)),
        );
        result = Math.max(1, Number(nightPct) * moonPhaseFactor * cloudFactor);
      } else {
        const effectiveCloudiness = Math.max(
          0,
          Math.min(1, cloudiness + (cloudStrength * cloudSimulationCoverage)),
        );
        const weatherFactor = Math.max(
          0.5,
          Math.min(1, 1 - (effectiveCloudiness * cloudWeatherWeight)),
        );
        const waveFactor = Math.max(
          0.35,
          Math.min(
            1,
            1 - (
              effectiveCloudiness
              * cloudStrength
              * (0.25 + (0.75 * wave))
              * cloudWaveStrength
            ),
          ),
        );
        cloudFactor = weatherFactor * waveFactor;
        result = base * priceFactor * cloudFactor;
      }
      basePoints.push({ time, value: Math.max(0, Math.min(100, base)) });
      resultPoints.push({ time, value: Math.max(0, Math.min(100, result)) });
      priceFactorPoints.push({ time, value: priceFactor * 100 });
      cloudFactorPoints.push({ time, value: cloudFactor * 100 });
      if (battery !== null) {
        batterySocPoints.push({ time, value: Math.max(0, Math.min(100, battery)) });
      }
    }

    const noonTime = start + (middayPeakMinute * 60 * 1000);
    return {
      batteryPath: this.pointPath(batterySocPoints, chart),
      basePath: this.pointPath(basePoints, chart),
      chart,
      cloudPath: this.pointPath(cloudFactorPoints, chart),
      end,
      now,
      noonX: chart.x(noonTime),
      noonY: chart.y(Math.max(0, Math.min(100, Number(dayPct) || 0))),
      pricePath: this.pointPath(priceFactorPoints, chart),
      resultArea: this.areaPath(resultPoints, chart),
      resultPath: this.pointPath(resultPoints, chart),
      start,
    };
  }

  timelineValueAt(points, time, fallback) {
    if (!points.length) {
      return fallback;
    }
    let value = points[0].value;
    for (const point of points) {
      if (point.time > time) {
        break;
      }
      value = point.value;
    }
    return this.numberOrNull(value) ?? fallback;
  }

  priceFactorAt(price, reference, ceiling, maxDimming, responseExponent, currentFactor) {
    if (price !== null && reference !== null && ceiling !== null && ceiling > reference) {
      const rawLoad = Math.max(0, Math.min(1, (price - reference) / (ceiling - reference)));
      const load = rawLoad ** responseExponent;
      return 1 - (load * maxDimming);
    }
    const fallback = this.numberOrNull(currentFactor);
    return fallback === null ? 1 : Math.max(0, Math.min(1, fallback));
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

  controlButton(configKey, label, service, confirmation = "") {
    const entity = this.config[configKey];
    if (!entity) {
      return "";
    }
    const confirmAttribute = confirmation
      ? ` data-confirm="${this.escape(confirmation)}"`
      : "";
    return `<button data-domain="switch" data-service="${service}" data-entity="${this.escape(entity)}"${confirmAttribute}>${this.escape(label)}</button>`;
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

  sunriseOffsetControl(entity, value) {
    if (!entity) {
      return "";
    }
    const offset = Math.max(-6, Math.min(6, Number(value) || 0));
    return `
      <label class="alc-duration alc-sunrise-offset">
        <span class="alc-duration-head">
          <span>Sonnenaufgang verschieben</span>
          <strong>${this.escape(this.formatSignedHours(offset))}</strong>
        </span>
        <input
          type="range"
          min="-6"
          max="6"
          step="0.25"
          value="${offset}"
          data-sunrise-offset="${this.escape(entity)}"
          aria-label="Sonnenaufgang in Stunden verschieben"
        />
      </label>
    `;
  }

  formatSignedHours(value) {
    const number = Number(value) || 0;
    const sign = number > 0 ? "+" : "";
    return `${sign}${number.toLocaleString("de-DE", { maximumFractionDigits: 2 })} h`;
  }

  transitionColorControls(
    sunriseStartRgbw,
    sunriseEndRgbw,
    sunsetStartRgbw,
    sunsetEndRgbw,
    configEntryId,
    sunriseDurationEntity,
    sunriseDuration,
    sunsetDurationEntity,
    sunsetDuration,
  ) {
    return `
      <div class="alc-color-grid">
        ${this.transitionColorEditor(
          "sunrise",
          "Sonnenaufgang",
          sunriseStartRgbw,
          sunriseEndRgbw,
          configEntryId,
          sunriseDurationEntity,
          sunriseDuration,
        )}
        ${this.transitionColorEditor(
          "sunset",
          "Sonnenuntergang",
          sunsetStartRgbw,
          sunsetEndRgbw,
          configEntryId,
          sunsetDurationEntity,
          sunsetDuration,
        )}
      </div>
    `;
  }

  transitionColorEditor(phase, title, startRgbw, endRgbw, configEntryId, durationEntity, durationValue) {
    const duration = Math.max(10, Math.min(240, Math.round(Number(durationValue) || (phase === "sunrise" ? 60 : 90))));
    return `
      <section class="alc-color-editor">
        <div class="alc-color-editor-title">${this.escape(title)}</div>
        ${durationEntity ? `
          <div class="alc-transition-duration">
            <span class="alc-duration-head"><span>Dauer</span><strong>10–240 Min.</strong></span>
            <div class="alc-duration-stepper">
              <button type="button" data-duration-delta="-5" data-duration-entity="${this.escape(durationEntity)}" aria-label="${this.escape(title)} fuenf Minuten kuerzer">−</button>
              <input type="number" min="10" max="240" step="5" value="${duration}" data-transition-duration="${this.escape(durationEntity)}" aria-label="Dauer ${this.escape(title)} in Minuten" />
              <button type="button" data-duration-delta="5" data-duration-entity="${this.escape(durationEntity)}" aria-label="${this.escape(title)} fuenf Minuten laenger">+</button>
            </div>
          </div>
        ` : ""}
        <div class="alc-color-points">
          ${this.rgbwEndpointEditor(`${phase}_start`, "Anfang", startRgbw, title, configEntryId)}
          ${this.rgbwEndpointEditor(`${phase}_end`, "Ende", endRgbw, title, configEntryId)}
        </div>
      </section>
    `;
  }

  rgbwEndpointEditor(endpoint, label, rgbw, title, configEntryId) {
    const channels = ["R", "G", "B", "W"];
    return `
      <div class="alc-color-point" data-rgbw-editor data-phase="${endpoint}" data-config-entry-id="${this.escape(configEntryId)}">
        <div class="alc-color-main">
          <span class="alc-color-swatch" data-rgbw-swatch style="background:${this.rgbwPreviewCss(rgbw)}"></span>
          <span class="alc-color-copy">
            <span class="alc-color-title">${this.escape(label)}</span>
            <span class="alc-color-values" data-rgbw-values>RGBW ${rgbw.join(" / ")}</span>
          </span>
        </div>
        ${channels.map((channel, index) => `
          <label class="alc-channel alc-channel-${channel.toLowerCase()}">
            <span class="alc-channel-label">${channel}</span>
            <input class="alc-channel-slider" type="range" min="0" max="255" step="1" value="${rgbw[index]}" data-rgbw-channel data-channel-index="${index}" aria-label="${channel}-Kanal ${this.escape(title)} ${this.escape(label)}" />
            <span class="alc-channel-value" data-channel-value="${index}">${rgbw[index]}</span>
          </label>
        `).join("")}
      </div>
    `;
  }

  previewTransitionColor(editor) {
    const rgbw = [...editor.querySelectorAll("[data-rgbw-channel]")]
      .sort((left, right) => Number(left.dataset.channelIndex) - Number(right.dataset.channelIndex))
      .map((input) => Math.max(0, Math.min(255, Math.round(Number(input.value) || 0))));
    editor.querySelectorAll("[data-channel-value]").forEach((value) => {
      value.textContent = String(rgbw[Number(value.dataset.channelValue)]);
    });
    const copy = editor.querySelector("[data-rgbw-values]");
    if (copy) {
      copy.textContent = `RGBW ${rgbw.join(" / ")}`;
    }
    const swatch = editor.querySelector("[data-rgbw-swatch]");
    if (swatch) {
      swatch.style.background = this.rgbwPreviewCss(rgbw);
    }
  }

  saveTransitionColor(editor) {
    const rgbw = [...editor.querySelectorAll("[data-rgbw-channel]")]
      .sort((left, right) => Number(left.dataset.channelIndex) - Number(right.dataset.channelIndex))
      .map((input) => Math.max(0, Math.min(255, Math.round(Number(input.value) || 0))));
    const data = {
      phase: editor.dataset.phase,
      rgbw_color: rgbw,
    };
    if (editor.dataset.configEntryId) {
      data.config_entry_id = editor.dataset.configEntryId;
    }
    this._hass.callService("aquarium_led_cockpit", "set_transition_color", data);
  }

  normalizeRgbw(value, fallback) {
    if (!Array.isArray(value) || value.length !== 4) {
      return [...fallback];
    }
    return value.map((channel) => Math.max(0, Math.min(255, Math.round(Number(channel) || 0))));
  }

  rgbwCss(rgbw) {
    return `rgb(${rgbw[0]}, ${rgbw[1]}, ${rgbw[2]})`;
  }

  rgbwPreviewCss(rgbw) {
    const white = Math.max(0, Math.min(255, Number(rgbw[3]) || 0));
    const red = Math.min(255, Number(rgbw[0]) + white);
    const green = Math.min(255, Number(rgbw[1]) + white);
    const blue = Math.min(255, Number(rgbw[2]) + white);
    return `rgb(${red}, ${green}, ${blue})`;
  }

  priceRuleLabel(attr) {
    const reason = attr.price_ignored_reason;
    if (reason === "night") {
      return "Pause: Nacht";
    }
    if (reason === "battery_full") {
      return "Pause: Speicher voll";
    }
    return attr.price_ignored ? "Pausiert" : "Aktiv";
  }

  celestialGeometry(time, sunrise, sunset) {
    const width = 720;
    const horizon = 138;
    const rise = this.parseMinute(sunrise, 360);
    const set = this.parseMinute(sunset, 1080);
    const minute = this.parseMinute(time, 720);
    const sunriseX = (rise / 1440) * width;
    const sunsetX = (set / 1440) * width;
    const nowX = (minute / 1440) * width;
    const dayDuration = Math.max(1, set - rise);
    const nightDuration = Math.max(1, (1440 - set) + rise);
    const isDay = minute >= rise && minute < set;

    let bodyX = nowX;
    let bodyY;
    if (isDay) {
      const progress = Math.max(0, Math.min(1, (minute - rise) / dayDuration));
      bodyY = horizon - (Math.sin(Math.PI * progress) * 98);
    } else {
      const unwrappedMinute = minute >= set ? minute : minute + 1440;
      const progress = Math.max(0, Math.min(1, (unwrappedMinute - set) / nightDuration));
      bodyY = horizon - (Math.sin(Math.PI * progress) * 72);
    }

    return {
      bodyX: bodyX.toFixed(1),
      bodyY: bodyY.toFixed(1),
      isDay,
      moonEveningArc: this.celestialArc(set, 1440, set, nightDuration, 72, width, horizon),
      moonMorningArc: this.celestialArc(1440, 1440 + rise, set, nightDuration, 72, width, horizon),
      nowX: nowX.toFixed(1),
      sunArc: this.celestialArc(rise, set, rise, dayDuration, 98, width, horizon),
      sunriseX: sunriseX.toFixed(1),
      sunsetX: sunsetX.toFixed(1),
    };
  }

  celestialArc(start, end, cycleStart, duration, amplitude, width, horizon) {
    const points = [];
    for (let index = 0; index <= 32; index += 1) {
      const unwrappedMinute = start + (((end - start) * index) / 32);
      const progress = Math.max(0, Math.min(1, (unwrappedMinute - cycleStart) / duration));
      const wrappedMinute = unwrappedMinute === 1440
        ? (start >= 1440 ? 0 : 1440)
        : unwrappedMinute % 1440;
      const x = (wrappedMinute / 1440) * width;
      const y = horizon - (Math.sin(Math.PI * progress) * amplitude);
      points.push(`${index === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`);
    }
    return points.join(" ");
  }

  profileAt(
    minute,
    sunrise,
    sunset,
    night,
    day,
    sunriseDuration = 60,
    sunsetDuration = 90,
    edgeFactor = 0.55,
    middayPeakMinute = 720,
  ) {
    const sunriseEnd = sunrise + sunriseDuration;
    const sunsetStart = sunset - sunsetDuration;
    const edge = day * edgeFactor;
    if (minute >= sunrise && minute < sunriseEnd) {
      return night + ((edge - night) * ((minute - sunrise) / sunriseDuration));
    }
    if (minute >= sunriseEnd && minute < sunsetStart) {
      const peak = Math.max(sunriseEnd, Math.min(sunsetStart, middayPeakMinute));
      const progress = minute <= peak
        ? Math.max(0, Math.min(1, (minute - sunriseEnd) / Math.max(1, peak - sunriseEnd)))
        : Math.max(0, Math.min(1, (sunsetStart - minute) / Math.max(1, sunsetStart - peak)));
      return edge + ((day - edge) * Math.sin(progress * Math.PI / 2));
    }
    if (minute >= sunsetStart && minute < sunset) {
      return edge + ((night - edge) * ((minute - sunsetStart) / sunsetDuration));
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
