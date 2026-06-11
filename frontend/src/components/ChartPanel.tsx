import React, { useState, useMemo, useRef } from "react";
import { QueryResponse } from "../api/client";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  LineChart, Line, AreaChart, Area, ScatterChart, Scatter,
  PieChart, Pie, Cell, ResponsiveContainer
} from "recharts";

const AMBER = "#e8963c";
const TEAL  = "#2dd4bf";
const PIE_COLORS = [AMBER, TEAL, "#a78bfa", "#f472b6", "#34d399", "#60a5fa"];

type ChartType = "bar" | "bar_h" | "line" | "area" | "scatter" | "histogram" | "pie";

const CHART_OPTIONS: { type: ChartType; label: string }[] = [
  { type: "bar",       label: "▬ Bar"       },
  { type: "bar_h",     label: "▮ H-Bar"     },
  { type: "line",      label: "〜 Line"      },
  { type: "area",      label: "◿ Area"      },
  { type: "scatter",   label: "⁙ Scatter"   },
  { type: "histogram", label: "▦ Histogram" },
  { type: "pie",       label: "◔ Pie"       },
];

interface Props {
  result: QueryResponse | null;
}

export default function ChartPanel({ result }: Props) {
  if (!result || !result.rows || !result.columns) return null;
  const { columns, rows, chart_advice: chartAdvice } = result;

  const rawSuggested = chartAdvice?.chart_type ?? "bar";
  const initial   = rawSuggested === "none" ? "bar" : (rawSuggested as ChartType);
  const [active, setActive] = useState<ChartType>(initial);
  const chartRef = useRef<HTMLDivElement>(null);

  const numericCols = useMemo(() =>
    columns.filter((_, ci) => rows.some(r => r[ci] !== null && !isNaN(Number(r[ci])))),
    [columns, rows]
  );

  const xCol = chartAdvice?.x_column ?? columns[0] ?? "";
  const yCol = chartAdvice?.y_column ?? numericCols[0] ?? "";
  const xIdx = columns.indexOf(xCol);
  const yIdx = columns.indexOf(yCol);

  const data = useMemo(() =>
    rows.slice(0, 100).map(row =>
      Object.fromEntries(columns.map((c, i) => [c, row[i]]))
    ), [rows, columns]
  );

  const histData = useMemo(() => {
    if (yIdx < 0) return [];
    const vals = rows.map(r => Number(r[yIdx])).filter(v => !isNaN(v));
    if (!vals.length) return [];
    const min = Math.min(...vals), max = Math.max(...vals);
    const step = (max - min) / 10 || 1;
    const buckets = Array.from({ length: 10 }, (_, i) => ({
      range: `${(min + i * step).toFixed(1)}`,
      count: 0,
    }));
    vals.forEach(v => {
      const i = Math.min(Math.floor((v - min) / step), 9);
      buckets[i].count++;
    });
    return buckets;
  }, [rows, yIdx]);

  const pieData = useMemo(() =>
    data.slice(0, 12).map(d => ({ name: String(d[xCol] ?? ""), value: Number(d[yCol] ?? 0) })),
    [data, xCol, yCol]
  );

  const ax = { fill: "#9ca3af", fontSize: 11 };
  const gr = { stroke: "#374151" };
  const tt = { backgroundColor: "#1a1f2e", border: "1px solid #374151", color: "#e5e7eb", fontSize: 12 };

  const downloadSVG = () => {
    const svg = chartRef.current?.querySelector("svg");
    if (!svg) return;
    const blob = new Blob([new XMLSerializer().serializeToString(svg)], { type: "image/svg+xml" });
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: `chart.svg` });
    a.click();
    URL.revokeObjectURL(a.href);
  };

  const downloadPNG = () => {
    const svg = chartRef.current?.querySelector("svg");
    if (!svg) return;
    const clone = svg.cloneNode(true) as SVGSVGElement;
    const serializer = new XMLSerializer();
    const svgStr = serializer.serializeToString(clone);
    const canvas = document.createElement("canvas");
    const rect = svg.getBoundingClientRect();
    canvas.width = rect.width * 2;
    canvas.height = rect.height * 2;
    const ctx = canvas.getContext("2d")!;
    ctx.scale(2, 2);
    const img = new Image();
    const blob = new Blob([svgStr], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    img.onload = () => {
      ctx.fillStyle = "#111827";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);
      canvas.toBlob((pngBlob) => {
        if (!pngBlob) return;
        const a = Object.assign(document.createElement("a"), {
          href: URL.createObjectURL(pngBlob),
          download: `chart.png`,
        });
        a.click();
        URL.revokeObjectURL(a.href);
      }, "image/png");
    };
    img.src = url;
  };

  if (!rows.length || !yCol) return (
    <p style={{ color: "#6b7280", fontSize: 13, marginTop: 16 }}>No chart available for this result.</p>
  );

  const renderChart = () => {
    const m = { top: 5, right: 20, left: 0, bottom: 60 };
    switch (active) {
      case "bar": return (
        <BarChart data={data} margin={m}>
          <CartesianGrid strokeDasharray="3 3" {...gr} />
          <XAxis dataKey={xCol} tick={ax} angle={-35} textAnchor="end" interval={0} />
          <YAxis tick={ax} /> <Tooltip contentStyle={tt} />
          <Bar dataKey={yCol} fill={AMBER} radius={[3,3,0,0]} />
        </BarChart>
      );
      case "bar_h": return (
        <BarChart data={data} layout="vertical" margin={{ top:5, right:20, left:80, bottom:5 }}>
          <CartesianGrid strokeDasharray="3 3" {...gr} />
          <XAxis type="number" tick={ax} /> <YAxis dataKey={xCol} type="category" tick={ax} width={75} />
          <Tooltip contentStyle={tt} /> <Bar dataKey={yCol} fill={TEAL} radius={[0,3,3,0]} />
        </BarChart>
      );
      case "line": return (
        <LineChart data={data} margin={m}>
          <CartesianGrid strokeDasharray="3 3" {...gr} />
          <XAxis dataKey={xCol} tick={ax} angle={-35} textAnchor="end" interval={0} />
          <YAxis tick={ax} /> <Tooltip contentStyle={tt} />
          <Line type="monotone" dataKey={yCol} stroke={AMBER} strokeWidth={2} dot={false} />
        </LineChart>
      );
      case "area": return (
        <AreaChart data={data} margin={m}>
          <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={AMBER} stopOpacity={0.3}/>
            <stop offset="95%" stopColor={AMBER} stopOpacity={0}/>
          </linearGradient></defs>
          <CartesianGrid strokeDasharray="3 3" {...gr} />
          <XAxis dataKey={xCol} tick={ax} angle={-35} textAnchor="end" interval={0} />
          <YAxis tick={ax} /> <Tooltip contentStyle={tt} />
          <Area type="monotone" dataKey={yCol} stroke={AMBER} fill="url(#g)" strokeWidth={2} />
        </AreaChart>
      );
      case "scatter": return (
        <ScatterChart margin={{ top:5, right:20, left:0, bottom:5 }}>
          <CartesianGrid strokeDasharray="3 3" {...gr} />
          <XAxis dataKey={xCol} tick={ax} /> <YAxis dataKey={yCol} tick={ax} />
          <Tooltip contentStyle={tt} /> <Scatter data={data} fill={TEAL} opacity={0.7} />
        </ScatterChart>
      );
      case "histogram": return (
        <BarChart data={histData} margin={{ top:5, right:20, left:0, bottom:5 }}>
          <CartesianGrid strokeDasharray="3 3" {...gr} />
          <XAxis dataKey="range" tick={ax} /> <YAxis tick={ax} />
          <Tooltip contentStyle={tt} /> <Bar dataKey="count" fill={AMBER} radius={[3,3,0,0]} />
        </BarChart>
      );
      case "pie": return (
        <PieChart>
          <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%"
            outerRadius={120} label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}>
            {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
          </Pie>
          <Tooltip contentStyle={tt} />
        </PieChart>
      );
    }
  };

  return (
    <div style={{ marginTop: 20 }}>
      {/* Header */}
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:12 }}>
        <span style={{ fontSize:13, color:"#9ca3af" }}>
          {chartAdvice?.title ?? `${yCol} by ${xCol}`}
          {rawSuggested !== "none" && <span style={{ marginLeft:8, fontSize:11, color:"#4b5563" }}>(AI: {rawSuggested})</span>}
        </span>
        <div style={{ display:"flex", gap:6 }}>
          <button onClick={downloadPNG} style={{
            background:"none", border:"1px solid #374151", borderRadius:6,
            color:"#9ca3af", fontSize:11, padding:"4px 10px", cursor:"pointer"
          }}>↓ PNG</button>
          <button onClick={downloadSVG} style={{
            background:"none", border:"1px solid #374151", borderRadius:6,
            color:"#9ca3af", fontSize:11, padding:"4px 10px", cursor:"pointer"
          }}>↓ SVG</button>
        </div>
      </div>
      {/* Toggle */}
      <div style={{ display:"flex", gap:4, marginBottom:14, flexWrap:"wrap" }}>
        {CHART_OPTIONS.map(({ type, label }) => (
          <button key={type} onClick={() => setActive(type)} style={{
            background: active===type ? "#e8963c22" : "none",
            border: `1px solid ${active===type ? AMBER : "#374151"}`,
            borderRadius:6, color: active===type ? AMBER : "#6b7280",
            fontSize:12, padding:"5px 12px", cursor:"pointer"
          }}>{label}</button>
        ))}
      </div>
      {/* Chart */}
      <div ref={chartRef} style={{ width:"100%", height:340, background:"#111827", borderRadius:8, padding:"12px 8px" }}>
        <ResponsiveContainer width="100%" height="100%">
          {renderChart() as React.ReactElement}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
