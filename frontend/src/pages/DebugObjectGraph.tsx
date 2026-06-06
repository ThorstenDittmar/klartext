/**
 * Debug Object Graph — not in normal navigation.
 *
 * Renders all live domain objects for the current user as an interactive
 * React Flow graph. Nodes show class name + field values; edges show
 * field-name labels. Colors indicate domain group: User = gray,
 * Narrativ domain = green, Wirkgefüge domain = blue.
 *
 * Route: /debug/objects
 */

import { memo, useEffect, useMemo, useState, useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Handle,
  Position,
  type Node,
  type Edge,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { api, type DebugNode, type DebugEdge } from "../lib/api";

// ---------------------------------------------------------------------------
// Domain classification
// ---------------------------------------------------------------------------

type DomainGroup = "user" | "narrativ" | "wirkgefuege" | "unknown";

const CLASS_DOMAIN: Record<string, DomainGroup> = {
  User: "user",
  Narrative: "narrativ",
  Scene: "narrativ",
  Actor: "narrativ",
  Claim: "narrativ",
  CausalModel: "wirkgefuege",
  Slot: "wirkgefuege",
  CausalRelation: "wirkgefuege",
  Axiom: "wirkgefuege",
};

const CLASS_ROW: Record<string, number> = {
  User: 0,
  Narrative: 1,
  Scene: 2,
  Actor: 3,
  Claim: 4,
  CausalModel: 5,
  Slot: 6,
  CausalRelation: 7,
  Axiom: 8,
};

function getDomain(className: string): DomainGroup {
  return CLASS_DOMAIN[className] ?? "unknown";
}

function getRow(className: string): number {
  return CLASS_ROW[className] ?? Object.keys(CLASS_ROW).length;
}

// ---------------------------------------------------------------------------
// Node styles
// ---------------------------------------------------------------------------

interface DomainStyle {
  bg: string;
  border: string;
  headerBg: string;
  headerColor: string;
}

const DOMAIN_STYLE: Record<DomainGroup, DomainStyle> = {
  user: {
    bg: "var(--color-bg-subtle)",
    border: "var(--color-border)",
    headerBg: "var(--color-border)",
    headerColor: "var(--color-text-secondary)",
  },
  narrativ: {
    bg: "var(--color-green-bg)",
    border: "var(--color-green-text)",
    headerBg: "var(--color-green-text)",
    headerColor: "var(--color-text-inverse)",
  },
  wirkgefuege: {
    bg: "var(--color-blue-bg)",
    border: "var(--color-blue-text)",
    headerBg: "var(--color-blue-text)",
    headerColor: "var(--color-text-inverse)",
  },
  unknown: {
    bg: "var(--color-bg-subtle)",
    border: "var(--color-border)",
    headerBg: "var(--color-border)",
    headerColor: "var(--color-text-secondary)",
  },
};

// ---------------------------------------------------------------------------
// Custom node component
// ---------------------------------------------------------------------------

// React Flow requires node data to extend Record<string, unknown>.
// DebugNode from api.ts doesn't have an index signature, so we use an
// intersection type that satisfies both the React Flow constraint and
// our own domain shape.
type DebugNodeData = {
  id: string;
  class_name: string;
  fields: Record<string, unknown>;
  [key: string]: unknown;
};

type DebugGraphNode = Node<DebugNodeData, "debugNode">;

const DebugNodeComponent = memo(function DebugNodeComponent({
  data,
}: NodeProps<DebugGraphNode>) {
  const style = DOMAIN_STYLE[getDomain(data.class_name)];

  return (
    <div
      style={{
        background: style.bg,
        border: `1px solid ${style.border}`,
        borderRadius: 6,
        minWidth: 200,
        maxWidth: 240,
        fontSize: 11,
        boxShadow: "0 1px 4px rgba(0,0,0,.08)",
      }}
    >
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: style.border, width: 8, height: 8 }}
      />

      {/* Header */}
      <div
        style={{
          background: style.headerBg,
          color: style.headerColor,
          padding: "4px 8px",
          fontWeight: 600,
          fontSize: 12,
          borderRadius: "5px 5px 0 0",
        }}
      >
        {data.class_name}
      </div>

      {/* Fields */}
      <div style={{ padding: "6px 8px", display: "flex", flexDirection: "column", gap: 2 }}>
        {Object.entries(data.fields).map(([key, val]) => {
          const display = val == null ? "—" : String(val);
          const isTruncated = display.length > 40;
          return (
            <div
              key={key}
              style={{ display: "flex", gap: 4, alignItems: "baseline", lineHeight: 1.4 }}
            >
              <span
                style={{
                  color: "var(--color-text-tertiary)",
                  flexShrink: 0,
                  minWidth: 60,
                }}
              >
                {key}
              </span>
              <span
                style={{
                  color: "var(--color-text-primary)",
                  overflow: "hidden",
                  whiteSpace: isTruncated ? "normal" : "nowrap",
                  wordBreak: "break-word",
                }}
                title={display}
              >
                {isTruncated ? display.slice(0, 38) + "…" : display}
              </span>
            </div>
          );
        })}
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: style.border, width: 8, height: 8 }}
      />
    </div>
  );
});

// Must be defined outside the component so React Flow doesn't recreate
// the node type on every render and cause an infinite loop.
const NODE_TYPES = { debugNode: DebugNodeComponent };

// ---------------------------------------------------------------------------
// Layout computation
// ---------------------------------------------------------------------------

const NODE_WIDTH = 230;
const NODE_H_GAP = 50;
const ROW_HEIGHT = 160;

function computeLayout(apiNodes: DebugNode[]): DebugGraphNode[] {
  // Group nodes by class_name to determine x positions within each row
  const groups: Record<string, DebugNode[]> = {};
  for (const n of apiNodes) {
    if (!groups[n.class_name]) groups[n.class_name] = [];
    groups[n.class_name].push(n);
  }

  const result: DebugGraphNode[] = [];
  for (const [className, members] of Object.entries(groups)) {
    const rowY = getRow(className) * ROW_HEIGHT;
    const totalW = members.length * NODE_WIDTH + (members.length - 1) * NODE_H_GAP;
    const startX = -totalW / 2;
    members.forEach((n, i) => {
      result.push({
        id: n.id,
        type: "debugNode",
        position: { x: startX + i * (NODE_WIDTH + NODE_H_GAP), y: rowY },
        // Cast: DebugNode satisfies DebugNodeData at runtime; the index
        // signature only exists to satisfy the React Flow Node constraint.
        data: n as unknown as DebugNodeData,
      });
    });
  }
  return result;
}

function toFlowEdges(apiEdges: DebugEdge[]): Edge[] {
  return apiEdges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    label: e.label,
    type: "smoothstep",
    style: { stroke: "var(--color-border)", strokeWidth: 1.5 },
    labelStyle: { fontSize: 10, fill: "var(--color-text-tertiary)" },
    labelBgStyle: { fill: "var(--color-bg)", fillOpacity: 0.85 },
  }));
}

// ---------------------------------------------------------------------------
// Filter helpers
// ---------------------------------------------------------------------------

type LayerFilter = "all" | "narrativ" | "wirkgefuege";

const DOMAIN_FOR_LAYER: Record<LayerFilter, DomainGroup[]> = {
  all: ["user", "narrativ", "wirkgefuege", "unknown"],
  narrativ: ["user", "narrativ"],
  wirkgefuege: ["user", "wirkgefuege"],
};

function filterGraph(
  apiNodes: DebugNode[],
  apiEdges: DebugEdge[],
  layerFilter: LayerFilter,
  hiddenClasses: Set<string>,
): { nodes: DebugNode[]; edges: DebugEdge[] } {
  const allowedDomains = new Set(DOMAIN_FOR_LAYER[layerFilter]);

  const visibleNodes = apiNodes.filter(
    (n) =>
      allowedDomains.has(getDomain(n.class_name)) &&
      !hiddenClasses.has(n.class_name),
  );
  const visibleIds = new Set(visibleNodes.map((n) => n.id));

  const visibleEdges = apiEdges.filter(
    (e) => visibleIds.has(e.source) && visibleIds.has(e.target),
  );

  return { nodes: visibleNodes, edges: visibleEdges };
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export default function DebugObjectGraph() {
  const [rawGraph, setRawGraph] = useState<{
    nodes: DebugNode[];
    edges: DebugEdge[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [layerFilter, setLayerFilter] = useState<LayerFilter>("all");
  const [hiddenClasses, setHiddenClasses] = useState<Set<string>>(new Set());

  const [nodes, setNodes, onNodesChange] = useNodesState<DebugGraphNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  // Fetch graph on mount
  useEffect(() => {
    setLoading(true);
    api.debug
      .getObjectGraph()
      .then((g) => {
        setRawGraph(g);
        setLoading(false);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : String(err));
        setLoading(false);
      });
  }, []);

  // All class names present in the current data (for checkboxes)
  const availableClasses = useMemo(() => {
    if (!rawGraph) return [];
    const seen = new Set<string>();
    for (const n of rawGraph.nodes) seen.add(n.class_name);
    return [...seen].sort((a, b) => getRow(a) - getRow(b));
  }, [rawGraph]);

  // Classes visible under current layer filter (for checkbox panel)
  const visibleClassesForFilter = useMemo(() => {
    const allowedDomains = new Set(DOMAIN_FOR_LAYER[layerFilter]);
    return availableClasses.filter((cls) => allowedDomains.has(getDomain(cls)));
  }, [availableClasses, layerFilter]);

  // Re-derive React Flow nodes/edges whenever raw data or filters change
  useEffect(() => {
    if (!rawGraph) return;
    const { nodes: filtered, edges: filteredEdges } = filterGraph(
      rawGraph.nodes,
      rawGraph.edges,
      layerFilter,
      hiddenClasses,
    );
    setNodes(computeLayout(filtered));
    setEdges(toFlowEdges(filteredEdges));
  }, [rawGraph, layerFilter, hiddenClasses, setNodes, setEdges]);

  // Reset hidden classes when layer filter changes (avoid leftover state)
  const handleLayerFilter = useCallback(
    (f: LayerFilter) => {
      setLayerFilter(f);
      setHiddenClasses(new Set());
    },
    [],
  );

  const toggleClass = useCallback((cls: string) => {
    setHiddenClasses((prev) => {
      const next = new Set(prev);
      if (next.has(cls)) next.delete(cls);
      else next.add(cls);
      return next;
    });
  }, []);

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  if (loading) {
    return (
      <div style={{ padding: 40, color: "var(--color-text-secondary)" }}>
        Lade Objektgraph…
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: 40, color: "var(--color-red-text)" }}>
        Fehler: {error}
      </div>
    );
  }

  const nodeCount = nodes.length;
  const edgeCount = edges.length;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      {/* ── Header ─────────────────────────────────────────────────── */}
      <div
        style={{
          padding: "12px 20px",
          borderBottom: "1px solid var(--color-border)",
          background: "var(--color-bg)",
          display: "flex",
          alignItems: "center",
          gap: 24,
          flexWrap: "wrap",
        }}
      >
        <div>
          <span
            style={{
              fontWeight: 700,
              fontSize: 14,
              color: "var(--color-text-primary)",
            }}
          >
            Debug: Objektgraph
          </span>
          <span
            style={{
              marginLeft: 12,
              fontSize: 12,
              color: "var(--color-text-tertiary)",
            }}
          >
            {nodeCount} Knoten · {edgeCount} Kanten
          </span>
        </div>

        {/* Layer filter buttons */}
        <div style={{ display: "flex", gap: 6 }}>
          {(["all", "narrativ", "wirkgefuege"] as LayerFilter[]).map((f) => (
            <button
              key={f}
              onClick={() => handleLayerFilter(f)}
              style={{
                padding: "4px 12px",
                fontSize: 12,
                borderRadius: 4,
                border: `1px solid ${layerFilter === f ? "var(--color-text-primary)" : "var(--color-border)"}`,
                background:
                  layerFilter === f
                    ? "var(--color-text-primary)"
                    : "var(--color-bg)",
                color:
                  layerFilter === f
                    ? "var(--color-text-inverse)"
                    : "var(--color-text-secondary)",
                cursor: "pointer",
                fontWeight: layerFilter === f ? 600 : 400,
              }}
            >
              {f === "all" ? "Alle" : f === "narrativ" ? "Narrativ" : "Wirkgefüge"}
            </button>
          ))}
        </div>

        {/* Class checkboxes */}
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {visibleClassesForFilter.map((cls) => {
            const style = DOMAIN_STYLE[getDomain(cls)];
            const checked = !hiddenClasses.has(cls);
            return (
              <label
                key={cls}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 5,
                  cursor: "pointer",
                  fontSize: 12,
                  color: checked
                    ? "var(--color-text-primary)"
                    : "var(--color-text-tertiary)",
                }}
              >
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleClass(cls)}
                  style={{ accentColor: style.border }}
                />
                <span
                  style={{
                    display: "inline-block",
                    width: 8,
                    height: 8,
                    borderRadius: 2,
                    background: style.headerBg,
                    marginRight: 2,
                  }}
                />
                {cls}
              </label>
            );
          })}
        </div>
      </div>

      {/* ── Graph canvas ─────────────────────────────────────────── */}
      <div style={{ flex: 1 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={NODE_TYPES}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.2}
          maxZoom={2}
          colorMode="light"
        >
          <Background gap={20} color="var(--color-border-subtle)" />
          <Controls />
          <MiniMap
            nodeColor={(n) => {
              const data = n.data as DebugNodeData;
              const style = DOMAIN_STYLE[getDomain(data?.class_name ?? "")];
              return style.headerBg;
            }}
            style={{
              border: "1px solid var(--color-border)",
              borderRadius: 6,
            }}
          />
        </ReactFlow>
      </div>
    </div>
  );
}
