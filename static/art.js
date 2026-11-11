/* Vendor illustrations: window.art(name, category) -> inline SVG string. */
(function () {
  const P = "#2a1633", P2 = "#3b2149", M = "#f2a900", R = "#c2255c", V = "#6a4c93", L = "#1f8a5b", W = "#fff", C = "#fff3d1", G = "#d8cfe0";

  const lights = y => {
    let s = `<path d="M0 ${y}Q80 ${y + 28} 160 ${y}T320 ${y}" fill="none" stroke="${P}" stroke-width="1.5"/>`;
    for (let x = 20, i = 0; x < 320; x += 40, i++) {
      const u = ((x % 160) - 80) / 80;
      s += `<circle cx="${x}" cy="${y + 14 * (1 - u * u) + 4}" r="4.5" fill="${[M, R, W][i % 3]}"/>`;
    }
    return s;
  };
  const steam = (x, y) => `<path d="M${x} ${y}q-6-8 0-16t0-16M${x + 14} ${y}q-6-8 0-16t0-16" fill="none" stroke="${W}" stroke-width="3" stroke-linecap="round" opacity=".8"/>`;
  const note = (x, y, c, s = 30) => `<text x="${x}" y="${y}" font-size="${s}" fill="${c}" font-family="Segoe UI Symbol,Arial">♪</text>`;
  const tree = (x, y, r) => `<rect x="${x - 4}" y="${y}" width="8" height="${160 - y}" fill="#7a4a1e"/><circle cx="${x}" cy="${y}" r="${r}" fill="${L}"/>`;
  const ground = (c, y = 160) => `<rect y="${y}" width="320" height="${200 - y}" fill="${c}"/>`;
  const table = c => `<rect y="150" width="320" height="50" fill="${c}"/>`;

  const D = {
    hall: c => ground("#cdbfd6") + `<rect x="70" y="84" width="180" height="76" fill="${W}"/><path d="M56 86L160 40l104 46z" fill="${c}"/>
      <rect x="145" y="114" width="30" height="46" rx="2" fill="${P}"/><g fill="${M}"><rect x="88" y="104" width="34" height="26"/><rect x="198" y="104" width="34" height="26"/></g><circle cx="160" cy="66" r="8" fill="${C}"/>`,
    banquet: c => ground("#cdbfd6") + `<rect x="40" y="72" width="240" height="88" fill="${c}"/><rect x="30" y="62" width="260" height="12" fill="${P}"/>
      <g fill="${C}"><path d="M62 160v-42a22 22 0 0144 0v42z"/><path d="M138 160v-42a22 22 0 0144 0v42z"/><path d="M214 160v-42a22 22 0 0144 0v42z"/></g>` + lights(18),
    ballroom: c => ground("#cdbfd6", 168) + `<rect x="66" y="74" width="188" height="86" fill="${C}"/><path d="M52 76L160 26l108 50z" fill="${c}"/>
      <g fill="${W}"><rect x="72" y="76" width="16" height="84"/><rect x="112" y="76" width="16" height="84"/><rect x="152" y="76" width="16" height="84"/><rect x="192" y="76" width="16" height="84"/><rect x="232" y="76" width="16" height="84"/></g>
      <rect x="52" y="158" width="216" height="10" fill="${P}"/><circle cx="160" cy="56" r="9" fill="${M}"/>`,
    lawn: c => `<ellipse cx="80" cy="190" rx="200" ry="60" fill="${L}"/><ellipse cx="270" cy="200" rx="160" ry="56" fill="#2c9c6a"/>
      <path d="M84 158L160 70l76 88z" fill="${W}"/><path d="M122 158l38-88 38 88z" fill="${c}"/><rect x="158" y="52" width="3" height="20" fill="${P}"/><path d="M161 52l18 7-18 7z" fill="${R}"/>` + lights(16),
    terrace: c => `<g fill="${P2}" opacity=".55"><rect x="10" y="70" width="44" height="90"/><rect x="62" y="96" width="36" height="64"/><rect x="226" y="84" width="40" height="76"/><rect x="274" y="56" width="38" height="104"/></g>
      <circle cx="252" cy="42" r="18" fill="${M}"/>` + ground(P, 150) + `<path d="M0 132h320M0 150h320" stroke="${P}" stroke-width="3"/><g stroke="${P}" stroke-width="2"><path d="M30 132v18M70 132v18M110 132v18M210 132v18M250 132v18M290 132v18"/></g>
      <path d="M112 104a48 40 0 0196 0z" fill="${c}"/><rect x="158" y="62" width="4" height="92" fill="${W}"/><rect x="132" y="136" width="56" height="6" rx="3" fill="${W}"/>`,
    farmhouse: c => ground(L) + tree(58, 96, 30) + tree(272, 108, 24) + `<rect x="110" y="102" width="100" height="58" fill="${W}"/><path d="M100 104l18-32 42-18 42 18 18 32z" fill="${c}"/>
      <rect x="148" y="122" width="24" height="38" fill="${P}"/><rect x="122" y="116" width="18" height="18" fill="${M}"/><rect x="180" y="116" width="18" height="18" fill="${M}"/>
      <path d="M0 150h100M220 150h100" stroke="${W}" stroke-width="4"/><g fill="${W}"><rect x="14" y="140" width="5" height="22"/><rect x="44" y="140" width="5" height="22"/><rect x="74" y="140" width="5" height="22"/><rect x="240" y="140" width="5" height="22"/><rect x="270" y="140" width="5" height="22"/><rect x="300" y="140" width="5" height="22"/></g>`,
    backyard: c => ground(L) + `<g fill="${c}">${[...Array(11)].map((_, i) => `<path d="M${6 + i * 29} 160V112l10-10 10 10v48z"/>`).join("")}</g>` + tree(262, 84, 34) +
      `<path d="M0 34Q160 78 320 34" fill="none" stroke="${P}" stroke-width="1.5"/>` + [...Array(9)].map((_, i) => { const x = 22 + i * 34, u = (x - 160) / 160, y = 34 + 22 * (1 - u * u); return `<path d="M${x - 9} ${y}h18l-9 18z" fill="${[M, R, W][i % 3]}"/>`; }).join(""),

    thali: c => table(P2) + `<circle cx="160" cy="104" r="80" fill="${G}"/><circle cx="160" cy="104" r="70" fill="#f6f2f8"/>
      ${[[112, 76, M], [146, 58, c], [184, 60, L], [214, 84, "#b5651d"]].map(([x, y, f]) => `<circle cx="${x}" cy="${y}" r="17" fill="${G}"/><circle cx="${x}" cy="${y}" r="13" fill="${f}"/>`).join("")}
      <circle cx="128" cy="130" r="26" fill="#e8c98a"/><circle cx="120" cy="124" r="2.5" fill="#b98f45"/><circle cx="136" cy="136" r="2.5" fill="#b98f45"/><ellipse cx="192" cy="134" rx="26" ry="20" fill="${W}"/>`,
    buffet: c => table(c) + [44, 126, 208].map(x => `<path d="M${x} 126a34 30 0 0168 0z" fill="#ece5f1"/><circle cx="${x + 34}" cy="94" r="5" fill="${P}"/><rect x="${x - 4}" y="126" width="76" height="16" rx="3" fill="${G}"/><path d="M${x + 6} 142v10M${x + 62} 142v10" stroke="${P}" stroke-width="3"/>` + steam(x + 27, 84)).join("") + `<rect y="150" width="320" height="6" fill="${P}" opacity=".25"/>`,
    snacks: c => table(P2) + `<ellipse cx="124" cy="150" rx="96" ry="24" fill="${G}"/><ellipse cx="124" cy="146" rx="84" ry="18" fill="#f6f2f8"/>
      <g fill="#d9a441" stroke="#b07c00" stroke-width="2" stroke-linejoin="round"><path d="M60 148l30-46 30 46z"/><path d="M104 150l32-50 32 50z"/><path d="M150 148l26-40 26 40z"/></g>
      <path d="M232 104h56v36a14 14 0 01-14 14h-28a14 14 0 01-14-14z" fill="${W}"/><path d="M288 114h8a10 10 0 010 20h-8" fill="none" stroke="${W}" stroke-width="6"/><rect x="236" y="108" width="48" height="8" fill="#b5651d"/>` + steam(252, 94),
    handi: c => table(P2) + `<path d="M92 96h136a8 8 0 010 16c0 34-20 52-68 52s-68-18-68-52a8 8 0 010-16z" fill="${c}"/><rect x="84" y="92" width="152" height="12" rx="6" fill="${P}"/>
      <path d="M118 92a42 26 0 0184 0z" fill="#b07c00"/><circle cx="160" cy="62" r="7" fill="${P}"/><path d="M104 130q56 22 112 0" fill="none" stroke="${M}" stroke-width="4"/>` + steam(250, 84) + steam(60, 84),
    bowl: c => table(P2) + `<path d="M76 92h168a84 76 0 01-168 0z" fill="${W}"/><rect x="130" y="164" width="60" height="8" rx="4" fill="${G}"/>
      <g fill="${L}"><ellipse cx="116" cy="84" rx="30" ry="14" transform="rotate(-24 116 84)"/><ellipse cx="204" cy="82" rx="32" ry="14" transform="rotate(20 204 82)"/><ellipse cx="160" cy="72" rx="26" ry="15"/></g>
      <circle cx="140" cy="88" r="11" fill="${R}"/><circle cx="184" cy="90" r="9" fill="${c}"/><circle cx="162" cy="92" r="7" fill="${M}"/>`,

    speaker: c => ground(P2, 164) + `<rect x="114" y="38" width="92" height="128" rx="10" fill="${P}"/><circle cx="160" cy="118" r="32" fill="${c}"/><circle cx="160" cy="118" r="13" fill="${P}"/><circle cx="160" cy="64" r="13" fill="${c}"/>` + note(52, 96, M, 44) + note(236, 76, R, 36) + note(256, 136, W, 28),
    dice: c => ground(P2, 164) + `<g transform="rotate(-12 116 112)"><rect x="76" y="72" width="80" height="80" rx="14" fill="${W}"/><g fill="${P}"><circle cx="98" cy="94" r="7"/><circle cx="116" cy="112" r="7"/><circle cx="134" cy="130" r="7"/></g></g>
      <g transform="rotate(14 214 104)"><rect x="178" y="68" width="72" height="72" rx="12" fill="${c}"/><g fill="${W}"><circle cx="198" cy="88" r="6"/><circle cx="230" cy="88" r="6"/><circle cx="198" cy="120" r="6"/><circle cx="230" cy="120" r="6"/></g></g>
      <g fill="${M}"><rect x="40" y="36" width="12" height="5" transform="rotate(30 46 38)"/><rect x="270" y="40" width="12" height="5" transform="rotate(-30 276 42)"/><circle cx="160" cy="36" r="4"/></g><rect x="100" y="30" width="10" height="5" fill="${R}" transform="rotate(-20 105 32)"/>`,
    mic: c => ground(P2, 164) + `<g transform="rotate(24 160 104)"><rect x="148" y="88" width="24" height="88" rx="10" fill="${P}"/><ellipse cx="160" cy="62" rx="30" ry="34" fill="${G}"/><path d="M132 52h56M130 66h60M134 80h52M150 30v64M170 30v64" stroke="${V}" stroke-width="2" opacity=".6"/><rect x="144" y="92" width="32" height="10" rx="3" fill="${c}"/></g>` + note(54, 84, M, 44) + note(92, 136, W, 28) + note(238, 150, c, 34),
    guitar: c => ground(P2, 164) + `<g transform="rotate(28 160 104)"><rect x="154" y="2" width="12" height="96" fill="#7a4a1e"/><rect x="149" y="-10" width="22" height="22" rx="4" fill="${P}"/><circle cx="160" cy="100" r="30" fill="#d9a441"/><circle cx="160" cy="142" r="42" fill="#d9a441"/><circle cx="160" cy="124" r="13" fill="${P}"/><rect x="146" y="156" width="28" height="6" fill="${P}"/><path d="M157 4v156M163 4v156" stroke="${W}" stroke-width="1" opacity=".7"/></g>` + note(44, 90, c, 40) + note(250, 70, M, 34),
    hat: c => ground(P2, 164) + `<rect x="112" y="62" width="96" height="86" fill="${P}"/><ellipse cx="160" cy="62" rx="48" ry="9" fill="${P2}"/><rect x="112" y="122" width="96" height="14" fill="${c}"/><ellipse cx="160" cy="150" rx="82" ry="13" fill="${P}"/>
      <g transform="rotate(-38 236 70)"><rect x="232" y="34" width="8" height="76" fill="${P}"/><rect x="232" y="34" width="8" height="16" fill="${W}"/></g>
      <g fill="${M}" font-family="Segoe UI Symbol,Arial"><text x="52" y="72" font-size="34">✦</text><text x="252" y="48" font-size="24">✦</text><text x="84" y="40" font-size="18">✦</text></g>`,
    dj: c => `<path d="M90 0L20 200h90z" fill="${M}" opacity=".35"/><path d="M230 0l70 200h-90z" fill="${c}" opacity=".35"/><path d="M160 0l-40 200h80z" fill="${W}" opacity=".25"/>` + ground(P2, 164) +
      `<rect x="44" y="98" width="232" height="70" rx="10" fill="${P}"/><circle cx="96" cy="132" r="27" fill="${P2}"/><circle cx="96" cy="132" r="8" fill="${M}"/><circle cx="224" cy="132" r="27" fill="${P2}"/><circle cx="224" cy="132" r="8" fill="${c}"/>
      <g stroke="${G}" stroke-width="3" stroke-linecap="round"><path d="M146 112v40M160 112v40M174 112v40"/></g><g fill="${M}"><rect x="142" y="120" width="8" height="6"/><rect x="156" y="138" width="8" height="6"/><rect x="170" y="126" width="8" height="6"/></g>`,
    drums: c => ground(P2, 164) + `<g stroke="${G}" stroke-width="3"><path d="M72 62v104M248 54v112"/></g><ellipse cx="72" cy="62" rx="36" ry="7" fill="${M}"/><ellipse cx="248" cy="54" rx="40" ry="8" fill="${M}"/>
      <rect x="100" y="76" width="50" height="30" rx="4" fill="${c}"/><rect x="170" y="76" width="50" height="30" rx="4" fill="${c}"/><ellipse cx="125" cy="76" rx="25" ry="6" fill="${W}"/><ellipse cx="195" cy="76" rx="25" ry="6" fill="${W}"/>
      <circle cx="160" cy="134" r="36" fill="${c}"/><circle cx="160" cy="134" r="28" fill="${W}"/><text x="160" y="142" text-anchor="middle" font-size="22" fill="${P}" font-family="Segoe UI Symbol,Arial">♪</text>`,
    jamun: c => table(P2) + `<path d="M76 104h168a84 62 0 01-168 0z" fill="${W}"/><rect x="130" y="162" width="60" height="8" rx="4" fill="${G}"/><ellipse cx="160" cy="104" rx="84" ry="12" fill="${M}" opacity=".55"/>
      ${[[122, 92], [160, 84], [198, 92], [142, 104], [180, 104]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="19" fill="#7a3b12"/><circle cx="${x - 6}" cy="${y - 7}" r="5" fill="#a85a26"/>`).join("")}`,
    icecream: c => table(P2) + `<circle cx="136" cy="88" r="28" fill="#f4a6c0"/><circle cx="184" cy="88" r="28" fill="${C}"/><circle cx="160" cy="62" r="28" fill="#7a3b12"/><circle cx="160" cy="32" r="8" fill="${R}"/>
      <path d="M106 100h108l-16 62h-76z" fill="${c}"/><path d="M106 100h108l-3 12H109z" fill="${W}" opacity=".5"/><rect x="216" y="56" width="10" height="50" rx="2" fill="#d9a441" transform="rotate(24 221 80)"/>`,
    fruit: c => table(P2) + `<ellipse cx="160" cy="146" rx="124" ry="26" fill="${G}"/><ellipse cx="160" cy="142" rx="110" ry="20" fill="#f6f2f8"/>
      <path d="M62 138a50 50 0 01100 0z" fill="${L}"/><path d="M70 138a42 42 0 0184 0z" fill="#e5484d"/><g fill="${P}"><circle cx="98" cy="122" r="2.5"/><circle cx="114" cy="112" r="2.5"/><circle cx="128" cy="126" r="2.5"/></g>
      <circle cx="192" cy="116" r="24" fill="${M}"/><circle cx="192" cy="116" r="17" fill="#ffc94d"/><g fill="${V}"><circle cx="236" cy="124" r="10"/><circle cx="252" cy="114" r="10"/><circle cx="254" cy="132" r="10"/><circle cx="240" cy="106" r="10"/></g>`,
    cake: c => table(P2) + `<ellipse cx="160" cy="158" rx="104" ry="14" fill="${G}"/><rect x="92" y="94" width="136" height="62" rx="8" fill="${C}"/><rect x="92" y="122" width="136" height="8" fill="${c}" opacity=".6"/>
      <path d="M92 104a8 8 0 018-10h120a8 8 0 018 10v6q-11 14-22 0t-22 0-22 0-22 0-22 0-26 0z" fill="${c}"/>
      ${[128, 160, 192].map(x => `<rect x="${x - 3}" y="62" width="6" height="32" fill="${W}"/><path d="M${x} 44q8 10 0 18q-8-8 0-18z" fill="${M}"/>`).join("")}`,
    stand: c => table(P2) + `<rect x="157" y="40" width="6" height="118" fill="${G}"/><circle cx="160" cy="38" r="7" fill="${P}"/>
      ${[[158, 96, [M, R, C, "#7a3b12", M, R]], [116, 64, [C, "#7a3b12", R, M]], [76, 36, [R, C]]].map(([y, rx, f]) =>
        f.map((col, i) => `<circle cx="${160 - rx + 16 + i * ((2 * rx - 32) / Math.max(1, f.length - 1))}" cy="${y - 14}" r="11" fill="${col}"/>`).join("") + `<ellipse cx="160" cy="${y}" rx="${rx}" ry="8" fill="${W}"/>`).join("")}`,

    balloons: c => ground(P2, 170) + [[110, 70, R], [160, 52, M], [210, 72, V], [136, 104, c], [186, 106, L]].map(([x, y, f]) =>
        `<path d="M${x} ${y + 30}L160 176" stroke="${P}" stroke-width="1.2"/><ellipse cx="${x}" cy="${y}" rx="24" ry="30" fill="${f}"/><ellipse cx="${x - 8}" cy="${y - 10}" rx="5" ry="8" fill="${W}" opacity=".5"/>`).join("") +
      `<path d="M0 14Q160 44 320 14" fill="none" stroke="${P}" stroke-width="1.5"/>` + [...Array(9)].map((_, i) => { const x = 22 + i * 34, u = (x - 160) / 160, y = 14 + 15 * (1 - u * u); return `<path d="M${x - 8} ${y}h16l-8 15z" fill="${[M, R, W][i % 3]}"/>`; }).join(""),
    drapes: c => ground(P2, 170) + `<path d="M0 0h130q-20 90-130 150z" fill="${c}"/><path d="M320 0H190q20 90 130 150z" fill="${c}"/><path d="M0 0h60Q40 80 0 120z" fill="${W}" opacity=".25"/><path d="M320 0h-60q20 80 60 120z" fill="${W}" opacity=".25"/>` +
      [112, 136, 160, 184, 208].map((x, i) => `<path d="M${x} 0v${96 + (i % 2) * 22}" stroke="${P}" stroke-width="1"/>` + [...Array(5)].map((_, j) => `<circle cx="${x}" cy="${18 + j * 22 + (i % 2) * 8}" r="4" fill="${j % 2 ? W : M}"/>`).join("")).join(""),
    garland: c => ground(P2, 170) + [0, 107, 214].map(x0 => [...Array(9)].map((_, i) => { const x = x0 + 6 + i * 12, u = (i - 4) / 4, y = 14 + 44 * (1 - u * u); return `<circle cx="${x}" cy="${y}" r="8" fill="${i % 2 ? "#e8743b" : M}"/>`; }).join("")).join("") +
      [107, 214].map(x => `<path d="M${x} 10v70" stroke="${L}" stroke-width="3"/>` + [30, 48, 66, 84].map((y, i) => `<circle cx="${x}" cy="${y}" r="7" fill="${i % 2 ? M : "#e8743b"}"/>`).join("")).join("") +
      `<circle cx="160" cy="150" r="30" fill="${c}"/><circle cx="160" cy="150" r="20" fill="${M}"/><circle cx="160" cy="150" r="9" fill="${W}"/>` + [0, 60, 120, 180, 240, 300].map(a => `<circle cx="160" cy="118" r="5" fill="${W}" transform="rotate(${a} 160 150)"/>`).join(""),
    booth: c => ground(P2, 170) + `<rect x="34" y="22" width="170" height="140" rx="6" fill="${c}"/><rect x="46" y="34" width="146" height="116" rx="4" fill="${C}"/>
      <g fill="${M}" font-family="Segoe UI Symbol,Arial"><text x="62" y="74" font-size="30">✦</text><text x="150" y="120" font-size="22">✦</text></g><circle cx="120" cy="92" r="24" fill="none" stroke="${R}" stroke-width="6"/>
      <path d="M252 112l-22 58M252 112l22 58M252 112v58" stroke="${P}" stroke-width="4"/><rect x="222" y="74" width="60" height="40" rx="6" fill="${P}"/><circle cx="252" cy="94" r="12" fill="${G}"/><circle cx="252" cy="94" r="6" fill="${P2}"/><rect x="262" y="66" width="14" height="8" fill="${P}"/>`,
    stage: c => `<path d="M70 0L20 150h110z" fill="${M}" opacity=".3"/><path d="M250 0l50 150H190z" fill="${W}" opacity=".25"/>` + ground(P2, 176) +
      `<rect x="70" y="36" width="180" height="104" rx="4" fill="${c}"/><circle cx="160" cy="88" r="30" fill="${C}"/><rect x="40" y="140" width="240" height="24" fill="${P}"/><rect x="56" y="164" width="208" height="12" fill="${P}" opacity=".7"/>
      ${[[58, 138], [262, 138]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="13" fill="${R}"/><circle cx="${x + 12}" cy="${y - 8}" r="10" fill="${M}"/><circle cx="${x - 10}" cy="${y - 10}" r="9" fill="${W}"/>`).join("")}`,
    arch: c => ground(L, 170) + `<path d="M84 170V96a76 76 0 01152 0v74" fill="none" stroke="#2c9c6a" stroke-width="20"/>` +
      [...Array(13)].map((_, i) => { const a = Math.PI * (1 - i / 12), x = 160 + 76 * Math.cos(a), y = 96 - 76 * Math.sin(a); return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${i % 2 ? 11 : 13}" fill="${[c, W, M][i % 3]}"/>`; }).join("") +
      [118, 142, 166].map((y, i) => `<circle cx="84" cy="${y}" r="11" fill="${[M, c, W][i]}"/><circle cx="236" cy="${y}" r="11" fill="${[W, M, c][i]}"/>`).join("") + `<path d="M160 20v30" stroke="${P}" stroke-width="2"/><path d="M144 50h32l-6 16h-20z" fill="${M}"/>`,
    mandap: c => ground(P2, 172) + `<path d="M48 62Q160 -10 272 62z" fill="${c}"/><path d="M48 62h224v10q-14 12-28 0t-28 0-28 0-28 0-28 0-28 0-28 0-28 0z" fill="${M}"/>
      ${[60, 126, 180, 246].map(x => `<rect x="${x}" y="72" width="14" height="100" fill="${C}"/><rect x="${x - 3}" y="72" width="20" height="8" fill="${M}"/><rect x="${x - 3}" y="164" width="20" height="8" fill="${M}"/>`).join("")}
      <path d="M74 72q30 40 0 96" fill="none" stroke="${W}" stroke-width="5" opacity=".7"/><path d="M246 72q-30 40 0 96" fill="none" stroke="${W}" stroke-width="5" opacity=".7"/><circle cx="160" cy="30" r="7" fill="${M}"/><rect x="140" y="150" width="40" height="22" rx="3" fill="${R}"/>`,
    noodles: c => table(P2) + `<path d="M76 100h168a84 66 0 01-168 0z" fill="${c}"/><rect x="130" y="162" width="60" height="8" rx="4" fill="${G}"/><ellipse cx="160" cy="100" rx="84" ry="14" fill="#f3d27a"/>
      <g fill="none" stroke="#d9a441" stroke-width="4" stroke-linecap="round"><path d="M96 98q16-14 32 0t32 0 32 0 32 0"/><path d="M104 106q14-10 28 0t28 0 28 0 28 0"/></g>
      <circle cx="130" cy="92" r="7" fill="${L}"/><circle cx="188" cy="94" r="7" fill="${R}"/><path d="M196 96L262 30M210 100l64-56" stroke="#7a4a1e" stroke-width="5" stroke-linecap="round"/>` + steam(120, 74),
    boho: c => ground(P2, 170) + `<rect x="196" y="24" width="96" height="120" rx="48" fill="${C}"/><path d="M212 40v96M228 30v108M244 26v112M260 30v108M276 40v96" stroke="#d9a441" stroke-width="2"/>
      ${[[60, 60, -14], [92, 40, -4], [124, 52, 8], [150, 76, 18]].map(([x, y, a]) => `<g transform="rotate(${a} ${x} 170)"><path d="M${x} 170V${y + 30}" stroke="#b98f45" stroke-width="3"/><ellipse cx="${x}" cy="${y}" rx="12" ry="34" fill="#e8c98a"/><ellipse cx="${x - 4}" cy="${y + 4}" rx="5" ry="24" fill="${W}" opacity=".5"/></g>`).join("")}
      <path d="M74 170h66l-8-26H82z" fill="${c}"/>`,
    candles: c => table(P2) + [[104, 78, 60], [150, 54, 84], [196, 90, 48]].map(([x, y, h]) => `<rect x="${x}" y="${y + 12}" width="30" height="${h}" rx="3" fill="${W}"/><path d="M${x + 15} ${y - 14}q9 12 0 22q-9-10 0-22z" fill="${M}"/><path d="M${x + 15} ${y + 6}v8" stroke="${P}" stroke-width="2"/>`).join("") +
      `<path d="M30 146q60-20 250 0" fill="none" stroke="${L}" stroke-width="4"/>` + [...Array(9)].map((_, i) => `<ellipse cx="${46 + i * 28}" cy="${138 - (i % 2) * 6 - (4 - Math.abs(i - 4)) * 2}" rx="12" ry="6" fill="${i % 2 ? L : "#2c9c6a"}" transform="rotate(${i % 2 ? 24 : -24} ${46 + i * 28} 136)"/>`).join(""),
    camera: c => ground(P2, 170) + `<rect x="80" y="62" width="160" height="100" rx="14" fill="${P}"/><rect x="108" y="46" width="52" height="22" rx="6" fill="${P}"/><rect x="196" y="74" width="28" height="14" rx="4" fill="${M}"/>
      <circle cx="160" cy="114" r="38" fill="${G}"/><circle cx="160" cy="114" r="28" fill="${c}"/><circle cx="160" cy="114" r="13" fill="${P}"/><circle cx="150" cy="104" r="6" fill="${W}" opacity=".7"/>
      <g fill="${M}" font-family="Segoe UI Symbol,Arial"><text x="36" y="66" font-size="30">✦</text><text x="258" y="50" font-size="22">✦</text><text x="266" y="130" font-size="16">✦</text></g>`,
    gift: c => ground(P2, 170) + `<rect x="92" y="88" width="136" height="82" rx="6" fill="${c}"/><rect x="84" y="70" width="152" height="26" rx="6" fill="${c}"/><rect x="84" y="70" width="152" height="26" rx="6" fill="${P}" opacity=".15"/>
      <rect x="150" y="70" width="20" height="100" fill="${M}"/><path d="M160 70q-44-44-52-12t52 12zM160 70q44-44 52-12t-52 12z" fill="${M}"/><circle cx="160" cy="68" r="9" fill="#ffc94d"/>
      <g fill="${W}" font-family="Segoe UI Symbol,Arial" opacity=".9"><text x="44" y="60" font-size="24">✦</text><text x="256" y="92" font-size="18">✦</text></g>`,
    plant: c => table(P2) + `<path d="M118 104h84l-10 60h-64z" fill="${c}"/><rect x="110" y="94" width="100" height="16" rx="5" fill="${c}"/><rect x="110" y="94" width="100" height="16" rx="5" fill="${W}" opacity=".3"/>
      ${[-60, -30, 0, 30, 60].map(a => `<ellipse cx="160" cy="62" rx="13" ry="36" fill="${a % 60 ? "#2c9c6a" : L}" transform="rotate(${a} 160 96)"/>`).join("")}`,
    mug: c => table(P2) + `<path d="M108 68h96v74a18 18 0 01-18 18h-60a18 18 0 01-18-18z" fill="${c}"/><path d="M204 86h14a20 20 0 010 40h-14" fill="none" stroke="${c}" stroke-width="12"/>
      <text x="156" y="128" text-anchor="middle" font-size="40" fill="${W}" font-family="Segoe UI Symbol,Arial">♥</text>` + steam(142, 56),
    none: () => ground(P2, 164) + `<circle cx="160" cy="100" r="46" fill="none" stroke="${G}" stroke-width="8"/><path d="M128 132l64-64" stroke="${G}" stroke-width="8"/>`,
  };

  const SKY = "#d9e9f4", DUSK = "#f6d5c3", NIGHT = "#4a2a5c", ROOM = "#ead9f0", WARM = "#ffe3a3", TBL = "#f0e4f4";
  const MAP = {
    "Backyard Party Plot": ["backyard", SKY, W], "Neighbourhood Community Hall": ["hall", SKY, R], "College Seminar Hall": ["hall", DUSK, V],
    "Sunset Terrace Cafe": ["terrace", DUSK, R], "Open Sky Garden Lawn": ["lawn", SKY, M], "Green Leaf Banquet": ["banquet", DUSK, L],
    "The Lotus Banquet": ["banquet", NIGHT, R], "Riverside Farmhouse": ["farmhouse", SKY, R], "Grand Orchid Ballroom": ["ballroom", NIGHT, V],
    "Tea, Snacks & Samosas": ["snacks", WARM], "Basic Veg Thali": ["thali", TBL, L], "Chicken Combo Meal": ["handi", WARM, "#b5651d"], "Jain Thali": ["thali", WARM, "#e8c98a"],
    "Classic Veg Buffet": ["buffet", ROOM, L], "Vegan Kitchen Combo": ["bowl", "#dff1e6", M], "Classic Non-Veg Buffet": ["buffet", WARM, R],
    "Jain Royal Buffet": ["buffet", DUSK, V], "Premium Veg Feast": ["thali", ROOM, R], "Vegan Gourmet Spread": ["bowl", ROOM, V], "Royal Non-Veg Feast": ["handi", ROOM, R],
    "DIY Playlist + Rented Speaker": ["speaker", ROOM, V], "Games & Emcee Host": ["dice", WARM, R], "Karaoke Setup": ["mic", DUSK, R], "Live Acoustic Duo": ["guitar", "#dff1e6", L],
    "Magician / Stand-up Act": ["hat", ROOM, R], "Professional DJ + Lights": ["dj", NIGHT, R], "Live Band": ["drums", DUSK, R], "No entertainment": ["none", ROOM], "No decor": ["none", ROOM], "No photography": ["none", ROOM], "No return gifts": ["none", ROOM],
    "South Indian Meals": ["thali", "#dff1e6", "#b5651d"], "South Indian Tiffin Buffet": ["thali", WARM, W], "Indo-Chinese Veg Combo": ["noodles", ROOM, R], "Indo-Chinese Non-Veg Combo": ["noodles", WARM, P],
    "Minimalist Greens & Candles": ["candles", "#eef1ea"], "Boho Pampas & Macrame": ["boho", DUSK, "#b5651d"],
    "Reels & Phone Content Creator": ["camera", WARM, R], "Candid Photographer (2 hrs)": ["camera", SKY, "#3b6fd8"], "Full Event Photographer": ["camera", ROOM, V],
    "Photo + Highlight Video": ["camera", DUSK, L], "Cinematic Photo & Film": ["camera", NIGHT, R],
    "Chocolate Favour Box": ["gift", WARM, "#7a3b12"], "Potted Succulent": ["plant", SKY, "#d9a441"], "Dry Fruit Pouch": ["gift", "#dff1e6", "#b07c00"],
    "Personalised Mug": ["mug", ROOM, R], "Scented Candle Set": ["candles", DUSK], "Premium Gift Hamper": ["gift", NIGHT, R], "No dessert": ["none", ROOM],
    "Gulab Jamun": ["jamun", WARM], "Ice Cream Cup": ["icecream", "#dff1e6", R], "Fresh Fruit Platter": ["fruit", SKY], "Jamun & Ice Cream Duo": ["icecream", WARM, V],
    "Coconut Ladoo & Sorbet": ["stand", "#dff1e6"], "Indian Sweets Trio": ["jamun", ROOM], "Celebration Cake & Sweets": ["cake", DUSK, R], "Live Dessert Counter": ["stand", ROOM],
    "Balloons & Banner": ["balloons", SKY, "#3b6fd8"], "Fairy Lights & Drapes": ["drapes", NIGHT, R], "Photo Booth & Backdrop": ["booth", WARM, R], "Marigold Floral": ["garland", "#fff3d1", R],
    "Themed Stage Setup": ["stage", NIGHT, V], "Premium Floral & Lighting": ["arch", SKY, R], "Royal Mandap & Drapes": ["mandap", DUSK, R],
  };
  const FALLBACK = { venue: ["hall", SKY, V], food: ["thali", TBL, L], dessert: ["cake", DUSK, R], decor: ["balloons", SKY, V], photography: ["camera", SKY, V], gifts: ["gift", WARM, R], entertainment: ["speaker", ROOM, V] };

  window.art = function (name, category) {
    const [kind, bg, c] = MAP[name] || FALLBACK[(category || "").toLowerCase()] || FALLBACK.venue;
    const label = String(name).replace(/[&<>"]/g, "");
    return `<svg viewBox="0 0 320 200" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Illustration of ${label}"><rect width="320" height="200" fill="${bg}"/>${D[kind](c || R)}</svg>`;
  };
})();
