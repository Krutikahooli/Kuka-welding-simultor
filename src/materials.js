/**
 * Industrial Metallurgy Database & Workpiece Joint Geometries for KUKA Robotic Welding.
 */

export const METALS = {
  carbon_steel: {
    id: 'carbon_steel',
    name: 'Mild Carbon Steel (A36)',
    code: 'A36 Structural Steel',
    roughness: 0.45,
    metalness: 0.75,
    color: '#475569',
    seamColor: '#ff5500',
    beadColor: '#f59e0b',
    gas: '82% Ar / 18% CO2',
    voltage: 24.2,
    current: 185.0,
    wireSpeed: 8.4,
    sparkColors: ['#ffffff', '#fbbf24', '#f97316', '#ffedd5'],
    arcGlow: '#00e5ff',
    arcCore: '#ffffff',
    desc: 'Standard industrial structural steel. High penetration, warm amber weld bead deposit.'
  },
  stainless_304: {
    id: 'stainless_304',
    name: 'Stainless Steel (304)',
    code: 'AISI 304 Food-Grade Stainless',
    roughness: 0.25,
    metalness: 0.92,
    color: '#94a3b8',
    seamColor: '#0ea5e9',
    beadColor: '#fde047',
    gas: '98% Ar / 2% O2',
    voltage: 23.0,
    current: 160.0,
    wireSpeed: 7.5,
    sparkColors: ['#ffffff', '#38bdf8', '#fbbf24', '#f8fafc'],
    arcGlow: '#38bdf8',
    arcCore: '#ffffff',
    desc: 'Commercial austenitic stainless steel. Smooth reflective weld bead with straw-tinted HAZ.'
  },
  stainless_316l: {
    id: 'stainless_316l',
    name: 'Stainless Steel (316L)',
    code: '316L Marine Stainless',
    roughness: 0.22,
    metalness: 0.95,
    color: '#a1a1aa',
    seamColor: '#d97706',
    beadColor: '#fbbf24',
    gas: '98% Ar / 2% CO2',
    voltage: 22.8,
    current: 165.0,
    wireSpeed: 7.2,
    sparkColors: ['#ffffff', '#38bdf8', '#fbbf24', '#f8fafc'],
    arcGlow: '#38bdf8',
    arcCore: '#ffffff',
    desc: 'Molybdenum-alloyed marine stainless. Low carbon prevents carbide precipitation.'
  },
  aluminum_6061: {
    id: 'aluminum_6061',
    name: 'Aluminum Alloy (6061-T6)',
    code: '6061-T6 Aerospace Aluminum',
    roughness: 0.35,
    metalness: 0.85,
    color: '#cbd5e1',
    seamColor: '#0284c7',
    beadColor: '#e2e8f0',
    gas: '100% Pure Argon',
    voltage: 21.5,
    current: 210.0,
    wireSpeed: 11.8,
    sparkColors: ['#ffffff', '#00f2fe', '#e0f2fe', '#ffffff'],
    arcGlow: '#00f2fe',
    arcCore: '#ffffff',
    desc: 'High thermal conductivity aerospace aluminum. Frosted pearl-silver bead with clean AC arc.'
  },
  aluminum_5083: {
    id: 'aluminum_5083',
    name: 'Aluminum Marine (5083-H116)',
    code: '5083 Marine High-Strength',
    roughness: 0.38,
    metalness: 0.82,
    color: '#b0bec5',
    seamColor: '#0369a1',
    beadColor: '#eceff1',
    gas: '75% Ar / 25% Helium',
    voltage: 23.2,
    current: 225.0,
    wireSpeed: 12.5,
    sparkColors: ['#ffffff', '#38bdf8', '#e2e8f0'],
    arcGlow: '#38bdf8',
    arcCore: '#ffffff',
    desc: 'Shipbuilding structural aluminum. Extreme resistance to seawater corrosion with high toughness.'
  },
  titanium_gr5: {
    id: 'titanium_gr5',
    name: 'Titanium Alloy (Ti-6Al-4V)',
    code: 'Grade 5 Titanium (Ti-6Al-4V)',
    roughness: 0.28,
    metalness: 0.92,
    color: '#64748b',
    seamColor: '#8b5cf6',
    beadColor: '#c084fc',
    gas: '99.999% Ultra-High Purity Ar',
    voltage: 19.5,
    current: 140.0,
    wireSpeed: 5.8,
    sparkColors: ['#ffffff', '#c084fc', '#67e8f9', '#fdf4ff'],
    arcGlow: '#a855f7',
    arcCore: '#ffffff',
    desc: 'Aerospace superalloy. Vibrant rainbow anodization heat tint (straw, purple, royal blue).'
  },
  copper_c101: {
    id: 'copper_c101',
    name: 'Pure Copper (C10100)',
    code: 'C10100 Oxygen-Free Electronic Copper',
    roughness: 0.22,
    metalness: 0.95,
    color: '#c2410c',
    seamColor: '#ea580c',
    beadColor: '#fb923c',
    gas: '100% Helium Shielding',
    voltage: 28.0,
    current: 260.0,
    wireSpeed: 10.5,
    sparkColors: ['#ffffff', '#fb923c', '#f97316'],
    arcGlow: '#f97316',
    arcCore: '#ffffff',
    desc: 'High thermal & electrical conductivity copper. Requires high voltage helium arc for deep penetration.'
  },
  brass_c360: {
    id: 'brass_c360',
    name: 'Naval Brass (C360)',
    code: 'C36000 Free-Cutting Brass',
    roughness: 0.25,
    metalness: 0.90,
    color: '#d97706',
    seamColor: '#b45309',
    beadColor: '#f59e0b',
    gas: '75% Ar / 25% CO2',
    voltage: 24.5,
    current: 190.0,
    wireSpeed: 8.8,
    sparkColors: ['#ffffff', '#fde047', '#f59e0b'],
    arcGlow: '#eab308',
    arcCore: '#ffffff',
    desc: 'Golden yellow copper-zinc alloy. Excellent machinability and bright lustrous appearance.'
  },
  inconel_718: {
    id: 'inconel_718',
    name: 'Inconel 718 Superalloy',
    code: 'Inconel 718 Nickel-Chromium',
    roughness: 0.32,
    metalness: 0.88,
    color: '#52525b',
    seamColor: '#d97706',
    beadColor: '#eab308',
    gas: '95% Ar / 5% H2',
    voltage: 23.5,
    current: 155.0,
    wireSpeed: 6.5,
    sparkColors: ['#ffffff', '#fde047', '#f59e0b', '#fafaf9'],
    arcGlow: '#eab308',
    arcCore: '#ffffff',
    desc: 'Extreme temperature turbine superalloy. High strength champagne-gold bead deposit.'
  },
  duplex_2205: {
    id: 'duplex_2205',
    name: 'Duplex Steel (2205)',
    code: '2205 Austenitic-Ferritic Duplex',
    roughness: 0.26,
    metalness: 0.94,
    color: '#71717a',
    seamColor: '#0284c7',
    beadColor: '#38bdf8',
    gas: '97% Ar / 3% N2',
    voltage: 24.0,
    current: 175.0,
    wireSpeed: 7.8,
    sparkColors: ['#ffffff', '#38bdf8', '#93c5fd'],
    arcGlow: '#0284c7',
    arcCore: '#ffffff',
    desc: 'High tensile oil & gas offshore alloy. 50/50 austenite-ferrite microstructure with extreme pitting resistance.'
  }
};

/**
 * Dense 36-point Smooth Circular Trajectory
 */
function generateCircleTrajectory() {
  const points = [
    { name: '1. Safe High Clearance Approach', x: 620, y: -72, z: 460, delay: 2000 },
    { name: '2. Vertical Touchdown (0° Seam)', x: 620, y: -72, z: 298, delay: 1400 }
  ];

  const rSeam = 72.0;
  for (let deg = 0; deg <= 360; deg += 10) {
    const rad = ((deg - 90) * Math.PI) / 180;
    points.push({
      name: `Arc Weld (${deg}°)`,
      x: +(620 + rSeam * Math.cos(rad)).toFixed(1),
      y: +(rSeam * Math.sin(rad)).toFixed(1),
      z: 298.0,
      delay: 650
    });
  }

  points.push({ name: '3. Crater Fill', x: 620, y: -72, z: 298, delay: 1500 });
  points.push({ name: '4. Safe High Retract', x: 620, y: -72, z: 460, delay: 1800 });
  points.push({ name: '5. Standby Home', x: 450, y: 0, z: 600, delay: 2000 });
  return points;
}

/**
 * Dense 40-point Smooth Square Box Trajectory (10 points per edge)
 */
function generateSquareTrajectory() {
  const points = [
    { name: '1. Safe High Clearance Approach', x: 550, y: -70, z: 460, delay: 2000 },
    { name: '2. Touchdown Corner SW', x: 550, y: -70, z: 298, delay: 1400 }
  ];

  // Edge 1: South Edge (X from 550 to 690, Y = -70)
  for (let i = 1; i <= 10; i++) {
    const frac = i / 10;
    points.push({
      name: `South Edge (${Math.round(frac * 100)}%)`,
      x: +(550 + 140 * frac).toFixed(1),
      y: -70.0,
      z: 298.0,
      delay: 600
    });
  }

  // Edge 2: East Edge (X = 690, Y from -70 to +70)
  for (let i = 1; i <= 10; i++) {
    const frac = i / 10;
    points.push({
      name: `East Edge (${Math.round(frac * 100)}%)`,
      x: 690.0,
      y: +(-70 + 140 * frac).toFixed(1),
      z: 298.0,
      delay: 600
    });
  }

  // Edge 3: North Edge (X from 690 to 550, Y = +70)
  for (let i = 1; i <= 10; i++) {
    const frac = i / 10;
    points.push({
      name: `North Edge (${Math.round(frac * 100)}%)`,
      x: +(690 - 140 * frac).toFixed(1),
      y: 70.0,
      z: 298.0,
      delay: 600
    });
  }

  // Edge 4: West Edge (X = 550, Y from +70 to -70)
  for (let i = 1; i <= 10; i++) {
    const frac = i / 10;
    points.push({
      name: `West Edge (${Math.round(frac * 100)}%)`,
      x: 550.0,
      y: +(70 - 140 * frac).toFixed(1),
      z: 298.0,
      delay: 600
    });
  }

  points.push({ name: '3. Crater Fill', x: 550, y: -70, z: 298, delay: 1500 });
  points.push({ name: '4. Safe High Retract', x: 550, y: -70, z: 460, delay: 1800 });
  points.push({ name: '5. Standby Home', x: 450, y: 0, z: 600, delay: 2000 });
  return points;
}

/**
 * Dense 40-point Smooth T-Joint Fillet Trajectory (20 points per pass)
 */
function generateTJointTrajectory() {
  const points = [
    { name: '1. Safe High Clearance Approach', x: 520, y: -16, z: 460, delay: 2000 },
    { name: '2. Touchdown Fillet Pass A', x: 520, y: -16, z: 298, delay: 1400 }
  ];

  // Pass A: Left Fillet (X from 520 to 720, Y = -16)
  for (let i = 1; i <= 20; i++) {
    const frac = i / 20;
    points.push({
      name: `Fillet Pass A (${Math.round(frac * 100)}%)`,
      x: +(520 + 200 * frac).toFixed(1),
      y: -16.0,
      z: 298.0,
      delay: 600
    });
  }

  // High flyby over the vertical plate to opposite side
  points.push({ name: '3. Lift Flyby Over Plate', x: 720, y: 16, z: 460, delay: 2000 });
  points.push({ name: '4. Touchdown Fillet Pass B', x: 720, y: 16, z: 298, delay: 1400 });

  // Pass B: Right Fillet (X from 720 to 520, Y = +16)
  for (let i = 1; i <= 20; i++) {
    const frac = i / 20;
    points.push({
      name: `Fillet Pass B (${Math.round(frac * 100)}%)`,
      x: +(720 - 200 * frac).toFixed(1),
      y: 16.0,
      z: 298.0,
      delay: 600
    });
  }

  points.push({ name: '5. Safe High Retract', x: 520, y: 16, z: 460, delay: 1800 });
  points.push({ name: '6. Standby Home', x: 450, y: 0, z: 600, delay: 2000 });
  return points;
}

/**
 * Dense 36-point Smooth Hexagonal Flange Trajectory (6 points per edge)
 */
function generateHexTrajectory() {
  const points = [
    { name: '1. Safe High Clearance Approach', x: 694, y: 0, z: 460, delay: 2000 },
    { name: '2. Touchdown Vertex 1 (0°)', x: 694, y: 0, z: 298, delay: 1400 }
  ];

  const vertices = [
    { x: 694.0, y: 0.0 },
    { x: 657.0, y: 64.0 },
    { x: 583.0, y: 64.0 },
    { x: 546.0, y: 0.0 },
    { x: 583.0, y: -64.0 },
    { x: 657.0, y: -64.0 },
    { x: 694.0, y: 0.0 }
  ];

  for (let v = 0; v < 6; v++) {
    const p1 = vertices[v];
    const p2 = vertices[v + 1];
    for (let s = 1; s <= 6; s++) {
      const frac = s / 6;
      points.push({
        name: `Hex Edge ${v + 1} (${Math.round(frac * 100)}%)`,
        x: +(p1.x + (p2.x - p1.x) * frac).toFixed(1),
        y: +(p1.y + (p2.y - p1.y) * frac).toFixed(1),
        z: 298.0,
        delay: 600
      });
    }
  }

  points.push({ name: '3. Crater Fill', x: 694, y: 0, z: 298, delay: 1500 });
  points.push({ name: '4. Safe High Retract', x: 694, y: 0, z: 460, delay: 1800 });
  points.push({ name: '5. Standby Home', x: 450, y: 0, z: 600, delay: 2000 });
  return points;
}

/**
 * 3D Workpiece Geometries & Joint Types (All Dense Uniform-Speed Trajectories)
 */
export const WORKPIECE_SHAPES = {
  circle_pipe: {
    id: 'circle_pipe',
    name: 'Circular Pipe Collar (ASME B31.3)',
    subtitle: 'Outside Circumferential Fillet Weld (R=72mm)',
    desc: 'Continuous uniform-speed circular fillet weld around outer pipe perimeter.',
    pipeRadius: 64,
    seamRadius: 72,
    trajectory: generateCircleTrajectory(),
    krlCode: `; KUKA KRL - NORMAL SPEED CIRCULAR PIPE WELD (R=72mm)
DEF CIRCULAR_PIPE_WELD()
  $VEL.CP = 0.08
  PTP {X 450.0, Y 0.0, Z 600.0}
  LIN {X 620.0, Y -72.0, Z 460.0}
  LIN {X 620.0, Y -72.0, Z 298.0}
  ARC_ON(VOLTAGE=24.2, CURRENT=185)
  CIRC {X 692.0, Y 0.0, Z 298.0} ; East Arc (90°)
  CIRC {X 620.0, Y 72.0, Z 298.0} ; North Arc (180°)
  CIRC {X 548.0, Y 0.0, Z 298.0} ; West Arc (270°)
  CIRC {X 620.0, Y -72.0, Z 298.0} ; South Arc (360°)
  WAIT SEC 1.2
  ARC_OFF()
  LIN {X 620.0, Y -72.0, Z 460.0}
  PTP {X 450.0, Y 0.0, Z 600.0}
END`
  },

  square_box: {
    id: 'square_box',
    name: 'Square Box Section (AWS D1.1)',
    subtitle: 'Outside 4-Corner Perimeter (140x140mm)',
    desc: 'Continuous uniform-speed 4-pass square contour fillet weld.',
    boxSize: 124,
    seamSize: 140,
    trajectory: generateSquareTrajectory(),
    krlCode: `; KUKA KRL - NORMAL SPEED SQUARE BOX WELD (140x140mm)
DEF SQUARE_BOX_WELD()
  $VEL.CP = 0.08
  PTP {X 450.0, Y 0.0, Z 600.0}
  LIN {X 550.0, Y -70.0, Z 460.0}
  LIN {X 550.0, Y -70.0, Z 298.0}
  ARC_ON(VOLTAGE=23.8, CURRENT=175)
  LIN {X 690.0, Y -70.0, Z 298.0} ; South Edge
  LIN {X 690.0, Y 70.0, Z 298.0}  ; East Edge
  LIN {X 550.0, Y 70.0, Z 298.0}  ; North Edge
  LIN {X 550.0, Y -70.0, Z 298.0} ; West Edge
  WAIT SEC 1.2
  ARC_OFF()
  LIN {X 550.0, Y -70.0, Z 460.0}
  PTP {X 450.0, Y 0.0, Z 600.0}
END`
  },

  t_fillet: {
    id: 't_fillet',
    name: 'T-Joint Stiffener Gusset (ISO 9692)',
    subtitle: 'Dual Fillet Welds (L=200mm)',
    desc: 'Continuous uniform-speed structural dual fillet weld passes.',
    trajectory: generateTJointTrajectory(),
    krlCode: `; KUKA KRL - NORMAL SPEED T-JOINT FILLET WELD
DEF T_JOINT_WELD()
  $VEL.CP = 0.08
  PTP {X 450.0, Y 0.0, Z 600.0}
  LIN {X 520.0, Y -16.0, Z 460.0}
  LIN {X 520.0, Y -16.0, Z 298.0}
  ARC_ON(VOLTAGE=24.5, CURRENT=190)
  LIN {X 720.0, Y -16.0, Z 298.0}
  ARC_OFF()
  LIN {X 720.0, Y 16.0, Z 460.0}
  LIN {X 720.0, Y 16.0, Z 298.0}
  ARC_ON(VOLTAGE=24.5, CURRENT=190)
  LIN {X 520.0, Y 16.0, Z 298.0}
  ARC_OFF()
  LIN {X 520.0, Y 16.0, Z 460.0}
  PTP {X 450.0, Y 0.0, Z 600.0}
END`
  },

  hex_flange: {
    id: 'hex_flange',
    name: 'Hexagonal Flange Collar (DIN 2501)',
    subtitle: '6-Sided Polygon (R=74mm)',
    desc: 'Continuous uniform-speed 6-sided hexagonal perimeter weld.',
    trajectory: generateHexTrajectory(),
    krlCode: `; KUKA KRL - NORMAL SPEED HEX FLANGE WELD
DEF HEX_FLANGE_WELD()
  $VEL.CP = 0.08
  PTP {X 450.0, Y 0.0, Z 600.0}
  LIN {X 694.0, Y 0.0, Z 460.0}
  LIN {X 694.0, Y 0.0, Z 298.0}
  ARC_ON(VOLTAGE=24.0, CURRENT=180)
  LIN {X 657.0, Y 64.0, Z 298.0}
  LIN {X 583.0, Y 64.0, Z 298.0}
  LIN {X 546.0, Y 0.0, Z 298.0}
  LIN {X 583.0, Y -64.0, Z 298.0}
  LIN {X 657.0, Y -64.0, Z 298.0}
  LIN {X 694.0, Y 0.0, Z 298.0}
  ARC_OFF()
  LIN {X 694.0, Y 0.0, Z 460.0}
  PTP {X 450.0, Y 0.0, Z 600.0}
END`
  }
};
