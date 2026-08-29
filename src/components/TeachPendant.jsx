import React, { useState } from 'react';
import { METALS, WORKPIECE_SHAPES } from '../materials';
import { Play, Square, AlertOctagon, Sliders, Sparkles, Activity, Cpu, ShieldCheck, Code, StepForward, Layers, Box, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function TeachPendant({
  targetPos,
  setTargetPos,
  isPoweredOn,
  isAutoCycle,
  toggleAutoCycle,
  triggerEstop,
  resetPowerOn,
  selectedMetalKey,
  setSelectedMetalKey,
  selectedShapeKey,
  setSelectedShapeKey,
  speedOverride,
  setSpeedOverride,
  jogStep,
  setJogStep,
  onJog,
  onPreset,
  jointAngles,
  logs,
  clearLogs,
  // Script Execution Engine Props
  krlCode,
  setKrlCode,
  isScriptRunning,
  currentScriptLine,
  runKrlScript,
  stopKrlScript,
  stepKrlScript,
  loadKrlTemplate
}) {
  const [activeTab, setActiveTab] = useState('motion'); // 'motion' | 'shapes' | 'code' | 'metals' | 'telemetry'
  const activeMetal = METALS[selectedMetalKey] || METALS.carbon_steel;
  const activeShape = WORKPIECE_SHAPES[selectedShapeKey] || WORKPIECE_SHAPES.circle_pipe;

  // Calibrated Collision-Free Presets
  const presets = [
    { label: '🏠 Standby Home', x: 450, y: 0, z: 600 },
    { label: '🎯 High Clearance Approach', x: 620, y: -72, z: 460 },
    { label: '🔥 Seam South (0°)', x: 620, y: -72, z: 298 },
    { label: '🔥 Seam East (90°)', x: 692, y: 0, z: 298 },
    { label: '🔥 Seam North (180°)', x: 620, y: 72, z: 298 },
    { label: '🔥 Seam West (270°)', x: 548, y: 0, z: 298 },
    { label: '🧹 Clean Station', x: 260, y: 380, z: 580 }
  ];

  // Calculate reach distance from shoulder pivot to detect max extension
  const dr = Math.sqrt(targetPos.x * targetPos.x + targetPos.y * targetPos.y) - 140;
  const dz = targetPos.z - 320;
  const reachDist = Math.sqrt(dr * dr + dz * dz);
  const isAtMaxReach = reachDist > 855; // (430 + 430 - 5)

  return (
    <div className="teach-pendant">
      {/* Tab Navigation */}
      <div className="pendant-tabs">
        <button
          onClick={() => setActiveTab('motion')}
          className={`pendant-tab-btn motion ${activeTab === 'motion' ? 'active' : ''}`}
        >
          <Sliders size={13} />
          MOTION
        </button>

        <button
          onClick={() => setActiveTab('shapes')}
          className={`pendant-tab-btn shapes ${activeTab === 'shapes' ? 'active' : ''}`}
          style={{ color: activeTab === 'shapes' ? '#38bdf8' : '' }}
        >
          <Box size={13} />
          JOINTS
        </button>

        <button
          onClick={() => setActiveTab('code')}
          className={`pendant-tab-btn code ${activeTab === 'code' ? 'active' : ''}`}
        >
          <Code size={13} />
          KRL CODE
        </button>

        <button
          onClick={() => setActiveTab('metals')}
          className={`pendant-tab-btn metals ${activeTab === 'metals' ? 'active' : ''}`}
        >
          <Sparkles size={13} />
          METALS ({Object.keys(METALS).length})
        </button>

        <button
          onClick={() => setActiveTab('telemetry')}
          className={`pendant-tab-btn telemetry ${activeTab === 'telemetry' ? 'active' : ''}`}
        >
          <Activity size={13} />
          STATUS
        </button>
      </div>

      {/* Main Tab Content */}
      <div className="pendant-content">
        {/* TAB 1: MOTION & JOG */}
        {activeTab === 'motion' && (
          <>
            {/* Target Coordinates */}
            <div className="pendant-section">
              <div className="section-header">
                <span>Target Position (mm)</span>
                <span style={{ fontSize: '10px', display: 'flex', alignItems: 'center', gap: '4px', color: isAtMaxReach ? '#f59e0b' : '#34d399', fontWeight: 700 }}>
                  {isAtMaxReach ? <AlertTriangle size={12} /> : <CheckCircle2 size={12} />}
                  {isAtMaxReach ? 'MAX REACH (CLAMPED)' : 'REACHABLE'}
                </span>
              </div>

              {[
                { axis: 'x', label: 'X (Reach)', val: targetPos.x, min: 180, max: 850, col: '#f87171' },
                { axis: 'y', label: 'Y (Sweep)', val: targetPos.y, min: -500, max: 500, col: '#34d399' },
                { axis: 'z', label: 'Z (Height)', val: targetPos.z, min: 180, max: 950, col: '#38bdf8' }
              ].map(({ axis, label, val, min, max, col }) => (
                <div key={axis} className="coord-row">
                  <span className="coord-label" style={{ color: col }}>{label}:</span>
                  <input
                    type="number"
                    value={val.toFixed(1)}
                    onChange={(e) =>
                      setTargetPos((p) => ({ ...p, [axis]: parseFloat(e.target.value) || 0 }))
                    }
                    className="coord-input"
                  />
                  <input
                    type="range"
                    min={min}
                    max={max}
                    step={1}
                    value={val}
                    onChange={(e) =>
                      setTargetPos((p) => ({ ...p, [axis]: parseFloat(e.target.value) }))
                    }
                    className="coord-slider"
                  />
                </div>
              ))}
            </div>

            {/* Micro-Jog Step & Matrix */}
            <div className="pendant-section">
              <div className="section-header">
                <span>Micro-Jog Axes</span>
                <div style={{ display: 'flex', gap: '4px' }}>
                  {[1, 10, 25, 50, 100].map((s) => (
                    <button
                      key={s}
                      onClick={() => setJogStep(s)}
                      style={{
                        padding: '2px 6px',
                        fontSize: '10px',
                        fontWeight: 700,
                        borderRadius: '4px',
                        border: 'none',
                        cursor: 'pointer',
                        background: jogStep === s ? '#0284c7' : '#1e293b',
                        color: jogStep === s ? '#ffffff' : '#94a3b8'
                      }}
                    >
                      {s}mm
                    </button>
                  ))}
                </div>
              </div>

              <div className="jog-grid">
                {[
                  { label: 'X- Retract', axis: 'x', dir: -1 },
                  { label: 'X+ Extend', axis: 'x', dir: 1 },
                  { label: 'Y- Left', axis: 'y', dir: -1 },
                  { label: 'Y+ Right', axis: 'y', dir: 1 },
                  { label: 'Z- Down', axis: 'z', dir: -1 },
                  { label: 'Z+ Up', axis: 'z', dir: 1 }
                ].map(({ label, axis, dir }) => (
                  <button
                    key={label}
                    onClick={() => onJog(axis, dir)}
                    disabled={!isPoweredOn}
                    className="jog-btn"
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Presets Grid */}
            <div className="pendant-section">
              <div className="section-header">
                <span>Calibrated Workcell Presets</span>
              </div>
              <div className="preset-grid">
                {presets.map((pr) => (
                  <button
                    key={pr.label}
                    onClick={() => onPreset(pr.x, pr.y, pr.z)}
                    disabled={!isPoweredOn}
                    className="preset-btn"
                  >
                    {pr.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Speed Override */}
            <div className="pendant-section" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '11px', fontWeight: 800 }}>Speed:</span>
              <input
                type="range"
                min={10}
                max={100}
                value={speedOverride}
                onChange={(e) => setSpeedOverride(parseInt(e.target.value))}
                style={{ flex: 1 }}
              />
              <span style={{ fontSize: '12px', fontFamily: 'monospace', fontWeight: 700, color: '#38bdf8', width: '45px', textAlign: 'right' }}>
                {speedOverride}%
              </span>
            </div>
          </>
        )}

        {/* TAB 2: WORKPIECE JOINT GEOMETRIES & SHAPES */}
        {activeTab === 'shapes' && (
          <>
            <div style={{ fontSize: '11px', color: '#94a3b8', lineHeight: '1.5', marginBottom: '8px' }}>
              Select a 3D workpiece joint geometry below to change the part fixture and calibrate the robotic welding trajectory:
            </div>

            {Object.values(WORKPIECE_SHAPES).map((shape) => (
              <button
                key={shape.id}
                onClick={() => setSelectedShapeKey(shape.id)}
                className={`metal-card ${selectedShapeKey === shape.id ? 'active' : ''}`}
                style={{ borderColor: selectedShapeKey === shape.id ? '#38bdf8' : '' }}
              >
                <div className="metal-card-header">
                  <span style={{ color: selectedShapeKey === shape.id ? '#38bdf8' : '' }}>{shape.name}</span>
                  <span style={{ fontSize: '10px', color: '#34d399', fontFamily: 'monospace' }}>
                    {shape.trajectory.length} Points
                  </span>
                </div>
                <div className="metal-desc" style={{ color: '#cbd5e1', fontWeight: 600 }}>{shape.subtitle}</div>
                <div className="metal-desc">{shape.desc}</div>
              </button>
            ))}
          </>
        )}

        {/* TAB 3: KRL CODE PROGRAMMING & SCRIPTING */}
        {activeTab === 'code' && (
          <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <span style={{ fontSize: '11px', fontWeight: 800, color: '#38bdf8' }}>KRL SCRIPT EDITOR</span>
              <div style={{ display: 'flex', gap: '4px' }}>
                <button
                  onClick={() => loadKrlTemplate('circle_pipe')}
                  style={{ fontSize: '9px', background: '#1e293b', color: '#38bdf8', padding: '3px 6px', borderRadius: '4px', border: '1px solid rgba(56, 189, 248, 0.3)', cursor: 'pointer' }}
                >
                  ⭕ Pipe
                </button>
                <button
                  onClick={() => loadKrlTemplate('square_box')}
                  style={{ fontSize: '9px', background: '#1e293b', color: '#f59e0b', padding: '3px 6px', borderRadius: '4px', border: '1px solid rgba(245, 158, 11, 0.3)', cursor: 'pointer' }}
                >
                  ⏹️ Square
                </button>
                <button
                  onClick={() => loadKrlTemplate('t_fillet')}
                  style={{ fontSize: '9px', background: '#1e293b', color: '#34d399', padding: '3px 6px', borderRadius: '4px', border: '1px solid rgba(52, 211, 153, 0.3)', cursor: 'pointer' }}
                >
                  📐 T-Joint
                </button>
                <button
                  onClick={() => loadKrlTemplate('hex_flange')}
                  style={{ fontSize: '9px', background: '#1e293b', color: '#c084fc', padding: '3px 6px', borderRadius: '4px', border: '1px solid rgba(192, 132, 252, 0.3)', cursor: 'pointer' }}
                >
                  🔷 Hex
                </button>
              </div>
            </div>

            {/* Code Editor Box */}
            <div style={{ background: '#07090e', borderRadius: '10px', border: '1px solid var(--border-color)', padding: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '4px', fontSize: '10px', color: '#94a3b8', fontFamily: 'monospace' }}>
                <span>PROGRAM: {activeShape.id.toUpperCase()}_WELD.SRC</span>
                <span>STATUS: {isScriptRunning ? `LINE ${currentScriptLine + 1}` : 'IDLE'}</span>
              </div>
              <textarea
                value={krlCode}
                onChange={(e) => setKrlCode(e.target.value)}
                disabled={isScriptRunning}
                rows={11}
                style={{
                  width: '100%',
                  background: 'transparent',
                  color: '#34d399',
                  fontFamily: 'Consolas, "JetBrains Mono", monospace',
                  fontSize: '11px',
                  border: 'none',
                  outline: 'none',
                  resize: 'vertical',
                  lineHeight: '1.4'
                }}
              />
            </div>

            {/* Script Execution Toolbar */}
            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                onClick={runKrlScript}
                disabled={!isPoweredOn || isScriptRunning}
                style={{
                  flex: 1,
                  padding: '10px',
                  background: '#0284c7',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: 800,
                  fontSize: '11px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  cursor: isPoweredOn && !isScriptRunning ? 'pointer' : 'not-allowed',
                  opacity: !isPoweredOn || isScriptRunning ? 0.4 : 1
                }}
              >
                <Play size={14} />
                RUN KRL SCRIPT
              </button>

              <button
                onClick={stepKrlScript}
                disabled={!isPoweredOn}
                style={{
                  padding: '10px 14px',
                  background: '#1e293b',
                  color: '#38bdf8',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  borderRadius: '8px',
                  fontWeight: 800,
                  fontSize: '11px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '4px',
                  cursor: isPoweredOn ? 'pointer' : 'not-allowed'
                }}
              >
                <StepForward size={14} />
                STEP
              </button>

              <button
                onClick={stopKrlScript}
                disabled={!isScriptRunning}
                style={{
                  padding: '10px 14px',
                  background: '#d97706',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: 800,
                  fontSize: '11px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '4px',
                  cursor: isScriptRunning ? 'pointer' : 'not-allowed',
                  opacity: isScriptRunning ? 1 : 0.4
                }}
              >
                <Square size={14} />
                STOP
              </button>
            </div>
          </>
        )}

        {/* TAB 4: METALS & METALLURGY */}
        {activeTab === 'metals' && (
          <>
            <div style={{ fontSize: '11px', color: '#94a3b8', lineHeight: '1.5', marginBottom: '8px' }}>
              Choose from 10 industrial metallurgy alloys to configure PBR shaders, shielding gas, and power source parameters:
            </div>

            {Object.values(METALS).map((metal) => (
              <button
                key={metal.id}
                onClick={() => setSelectedMetalKey(metal.id)}
                className={`metal-card ${selectedMetalKey === metal.id ? 'active' : ''}`}
              >
                <div className="metal-card-header">
                  <span>{metal.name}</span>
                  <span className="metal-dot" style={{ backgroundColor: metal.color }}></span>
                </div>
                <div className="metal-desc">{metal.desc}</div>
                <div className="metal-specs">
                  <span>Gas: {metal.gas}</span>
                  <span>{metal.voltage}V / {metal.current}A</span>
                </div>
              </button>
            ))}
          </>
        )}

        {/* TAB 5: TELEMETRY & DIAGNOSTICS */}
        {activeTab === 'telemetry' && (
          <>
            {/* Joint Angles Readout */}
            <div className="pendant-section">
              <div className="section-header">
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Cpu size={14} />
                  6-Axis Joint Positions
                </span>
              </div>

              {['A1', 'A2', 'A3', 'A4', 'A5', 'A6'].map((ax) => {
                const deg = jointAngles?.[ax] || 0;
                const pct = Math.min(100, Math.max(0, ((deg + 180) / 360) * 100));
                return (
                  <div key={ax} className="gauge-row">
                    <span className="gauge-axis">{ax}:</span>
                    <span className="gauge-val">{deg.toFixed(1)}°</span>
                    <div className="gauge-bar-track">
                      <div className="gauge-bar-fill" style={{ width: `${pct}%` }}></div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Fronius Arc Power Source Readout */}
            <div className="pendant-section">
              <div className="section-header">
                <span>Fronius Arc Power Source</span>
              </div>
              <div className="telemetry-grid">
                <div className="telemetry-cell">
                  <div className="telemetry-cell-title">Arc Voltage</div>
                  <div className="telemetry-cell-val" style={{ color: '#38bdf8' }}>
                    {isAutoCycle || isScriptRunning ? (activeMetal.voltage + (Math.random() * 0.8 - 0.4)).toFixed(1) : '0.0'} V
                  </div>
                </div>
                <div className="telemetry-cell">
                  <div className="telemetry-cell-title">Weld Current</div>
                  <div className="telemetry-cell-val" style={{ color: '#f59e0b' }}>
                    {isAutoCycle || isScriptRunning ? (activeMetal.current + (Math.random() * 6 - 3)).toFixed(1) : '0.0'} A
                  </div>
                </div>
                <div className="telemetry-cell">
                  <div className="telemetry-cell-title">Wire Feed</div>
                  <div className="telemetry-cell-val" style={{ color: '#34d399' }}>
                    {isAutoCycle || isScriptRunning ? activeMetal.wireSpeed : '0.0'} m/min
                  </div>
                </div>
                <div className="telemetry-cell">
                  <div className="telemetry-cell-title">Shield Gas</div>
                  <div className="telemetry-cell-val" style={{ color: '#c084fc', fontSize: '11px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {activeMetal.gas}
                  </div>
                </div>
              </div>
            </div>

            {/* KRL Communication Log */}
            <div className="pendant-section">
              <div className="section-header">
                <span>KRL Event Console</span>
                <button
                  onClick={clearLogs}
                  style={{ background: 'transparent', border: 'none', color: '#94a3b8', fontSize: '10px', cursor: 'pointer' }}
                >
                  Clear
                </button>
              </div>
              <div className="console-log-box">
                {logs.map((log, i) => (
                  <div key={i}>{log}</div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>

      {/* Action Footer Buttons */}
      <div className="pendant-footer">
        {!isPoweredOn && (
          <button onClick={resetPowerOn} className="btn-power-reset">
            <ShieldCheck size={16} />
            RESET SAFETY & POWER ON DRIVES
          </button>
        )}

        <div className="footer-btn-row">
          <button
            onClick={toggleAutoCycle}
            disabled={!isPoweredOn}
            className={`btn-auto-cycle ${isAutoCycle ? 'running' : ''}`}
          >
            {isAutoCycle ? (
              <>
                <Square size={16} />
                STOP (RETURN HOME)
              </>
            ) : (
              <>
                <Play size={16} />
                WELD {activeShape.id === 'circle_pipe' ? 'CIRCLE' : activeShape.id === 'square_box' ? 'SQUARE' : activeShape.id === 't_fillet' ? 'T-JOINT' : 'HEX'}
              </>
            )}
          </button>

          <button onClick={triggerEstop} className="btn-estop">
            <AlertOctagon size={16} />
            E-STOP
          </button>
        </div>
      </div>
    </div>
  );
}
