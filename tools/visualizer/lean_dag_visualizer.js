// src/js/modules/lean_dag_visualizer.js
// Interactive Topological DAG Visualizer & Tufte Proof-Walk Engine
// Strict 7-bit ASCII only (INV-001).

/**
 * LeanDagVisualizer converts Lean formalization dependency subgraphs
 * into topological layered layouts, WebGL buffers, and Tufte marginalia proof-walks.
 */
export class LeanDagVisualizer {
    constructor(options = {}) {
        this.nodes = new Map();
        this.edges = [];
        this.layers = [];
        this.options = {
            layerSpacing: options.layerSpacing || 140,
            nodeSpacing: options.nodeSpacing || 70,
            direction: options.direction || "LR", // "LR" (left-to-right) or "TB" (top-to-bottom)
            ...options
        };
    }

    /**
     * Load graph from formalization_breakdown.py --json-graph or lean_dependency_subgraph.
     * @param {Object} graphData - Object with nodes and edges
     */
    loadGraphData(graphData) {
        if (!graphData || typeof graphData !== "object") {
            throw new Error("Invalid graphData: expected object with nodes and edges");
        }
        this.nodes.clear();
        this.edges = [];

        const rawNodes = Array.isArray(graphData.nodes) ? graphData.nodes : [];
        for (const n of rawNodes) {
            this.nodes.set(n.id, {
                id: n.id,
                label: n.label || n.id,
                kind: n.kind || "theorem",
                module: n.module || "",
                line: n.line || 1,
                statement: n.statement || "",
                docstring: n.docstring || "",
                milestones: Array.isArray(n.milestones) ? n.milestones : [],
                uses: Array.isArray(n.uses) ? n.uses : [],
                layer: typeof n.layer === "number" ? n.layer : 0,
                x: 0,
                y: 0,
                inDegree: 0,
                outDegree: 0,
                status: n.status || "proven"
            });
        }

        const rawEdges = Array.isArray(graphData.edges) ? graphData.edges : [];
        for (const e of rawEdges) {
            const source = typeof e.source === "object" ? e.source.id : e.source;
            const target = typeof e.target === "object" ? e.target.id : e.target;
            if (this.nodes.has(source) && this.nodes.has(target)) {
                this.edges.push({ source, target });
                this.nodes.get(source).outDegree += 1;
                this.nodes.get(target).inDegree += 1;
            }
        }

        this.computeTopologicalLayers();
        this.layoutCoordinates();
        return this;
    }

    /**
     * Compute topological layering using Kahn's algorithm with longest path rank.
     */
    computeTopologicalLayers() {
        const inDeg = new Map();
        const adj = new Map();
        for (const [id] of this.nodes) {
            inDeg.set(id, 0);
            adj.set(id, []);
        }

        for (const e of this.edges) {
            inDeg.set(e.target, (inDeg.get(e.target) || 0) + 1);
            adj.get(e.source).push(e.target);
        }

        const rank = new Map();
        const queue = [];
        for (const [id, deg] of inDeg) {
            if (deg === 0) {
                queue.push(id);
                rank.set(id, 0);
            }
        }

        while (queue.length > 0) {
            const curr = queue.shift();
            const currRank = rank.get(curr);
            for (const nxt of adj.get(curr)) {
                const nextRank = Math.max(rank.get(nxt) || 0, currRank + 1);
                rank.set(nxt, nextRank);
                inDeg.set(nxt, inDeg.get(nxt) - 1);
                if (inDeg.get(nxt) === 0) {
                    queue.push(nxt);
                }
            }
        }

        const maxLayer = Math.max(0, ...Array.from(rank.values()));
        this.layers = Array.from({ length: maxLayer + 1 }, () => []);

        for (const [id, node] of this.nodes) {
            const l = rank.get(id) || 0;
            node.layer = l;
            this.layers[l].push(id);
        }
    }

    /**
     * Assign layout coordinates (x, y) based on layer index and intra-layer rank.
     */
    layoutCoordinates() {
        const { layerSpacing, nodeSpacing, direction } = this.options;
        for (let l = 0; l < this.layers.length; l++) {
            const nodeIds = this.layers[l];
            const layerHeight = nodeIds.length * nodeSpacing;
            for (let i = 0; i < nodeIds.length; i++) {
                const node = this.nodes.get(nodeIds[i]);
                if (direction === "LR") {
                    node.x = l * layerSpacing + 50;
                    node.y = (i - nodeIds.length / 2) * nodeSpacing + 400;
                } else {
                    node.x = (i - nodeIds.length / 2) * nodeSpacing + 600;
                    node.y = l * layerSpacing + 50;
                }
            }
        }
    }

    /**
     * Render a Tufte-style marginalia proof-walk card for a selected declaration.
     * @param {string} nodeId - Target node identifier
     * @returns {string} Clean HTML markup
     */
    renderTufteProofWalk(nodeId) {
        const node = this.nodes.get(nodeId);
        if (!node) return `<div class="tufte-proof-card error">Node not found: ${nodeId}</div>`;

        const incoming = this.edges.filter(e => e.target === nodeId).map(e => e.source);
        const outgoing = this.edges.filter(e => e.source === nodeId).map(e => e.target);

        let milestonesHtml = "";
        if (node.milestones && node.milestones.length > 0) {
            milestonesHtml = `
            <div class="proof-milestones">
                <span class="milestone-title">Proof Strategy Milestones:</span>
                <ul class="milestone-list">
                    ${node.milestones.map(m => `<li><code>${this.escapeHtml(m)}</code></li>`).join("")}
                </ul>
            </div>`;
        }

        let usesHtml = "";
        if (incoming.length > 0) {
            usesHtml = `
            <div class="proof-premises">
                <span class="premise-title">Uses Premises (\\uses{...}):</span>
                <div class="premise-tags">
                    ${incoming.map(p => `<span class="tufte-tag" data-node="${p}">${this.escapeHtml(p)}</span>`).join(" ")}
                </div>
            </div>`;
        }

        let dependentHtml = "";
        if (outgoing.length > 0) {
            dependentHtml = `
            <div class="proof-dependents">
                <span class="dependent-title">Enables Theorems:</span>
                <div class="dependent-tags">
                    ${outgoing.map(d => `<span class="tufte-tag" data-node="${d}">${this.escapeHtml(d)}</span>`).join(" ")}
                </div>
            </div>`;
        }

        return `
        <article class="tufte-proof-card" id="proof-card-${node.id}">
            <header class="card-header">
                <span class="declaration-kind badge-${node.kind}">${node.kind.toUpperCase()}</span>
                <h3 class="declaration-title">${this.escapeHtml(node.label)}</h3>
                <span class="layer-badge">Layer ${node.layer}</span>
            </header>
            <div class="card-body">
                <p class="declaration-meta">
                    <strong>Module:</strong> <code>${this.escapeHtml(node.module)}</code> : line ${node.line}
                </p>
                ${node.docstring ? `<div class="pedagogical-narrative">${this.escapeHtml(node.docstring)}</div>` : ""}
                ${node.statement ? `<pre class="lean-signature"><code>${this.escapeHtml(node.statement)}</code></pre>` : ""}
                ${milestonesHtml}
                ${usesHtml}
                ${dependentHtml}
            </div>
        </article>`.trim();
    }

    /**
     * Export graph as clean SVG markup.
     */
    exportSvg(options = {}) {
        const padding = 60;
        let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

        for (const [, n] of this.nodes) {
            if (n.x < minX) minX = n.x;
            if (n.y < minY) minY = n.y;
            if (n.x > maxX) maxX = n.x;
            if (n.y > maxY) maxY = n.y;
        }

        if (minX === Infinity) {
            minX = 0; minY = 0; maxX = 800; maxY = 600;
        }

        const width = maxX - minX + padding * 2;
        const height = maxY - minY + padding * 2;

        let edgeSvg = "";
        for (const e of this.edges) {
            const src = this.nodes.get(e.source);
            const tgt = this.nodes.get(e.target);
            const x1 = src.x - minX + padding;
            const y1 = src.y - minY + padding;
            const x2 = tgt.x - minX + padding;
            const y2 = tgt.y - minY + padding;
            edgeSvg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#888888" stroke-width="1.5" marker-end="url(#arrow)" />\n`;
        }

        let nodeSvg = "";
        for (const [, n] of this.nodes) {
            const cx = n.x - minX + padding;
            const cy = n.y - minY + padding;
            const color = n.kind === "theorem" ? "#2b6cb0" : "#2f855a";
            nodeSvg += `<g class="node" data-id="${n.id}">
                <circle cx="${cx}" cy="${cy}" r="12" fill="${color}" stroke="#ffffff" stroke-width="2"/>
                <text x="${cx + 16}" y="${cy + 4}" font-family="sans-serif" font-size="11" fill="#333333">${this.escapeHtml(n.label)}</text>
            </g>\n`;
        }

        return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">
            <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="22" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                    <path d="M 0 0 L 10 5 L 0 10 z" fill="#888888"/>
                </marker>
            </defs>
            <g class="edges">${edgeSvg}</g>
            <g class="nodes">${nodeSvg}</g>
        </svg>`;
    }

    /**
     * Format node and edge positions into WebGL instancing arrays.
     */
    toWebGLBuffer() {
        const nodePositions = new Float32Array(this.nodes.size * 2);
        const nodeColors = new Float32Array(this.nodes.size * 3);
        const idToIndex = new Map();

        let idx = 0;
        for (const [id, n] of this.nodes) {
            idToIndex.set(id, idx);
            nodePositions[idx * 2] = n.x;
            nodePositions[idx * 2 + 1] = n.y;
            if (n.kind === "theorem") {
                nodeColors[idx * 3] = 0.17; nodeColors[idx * 3 + 1] = 0.42; nodeColors[idx * 3 + 2] = 0.69;
            } else {
                nodeColors[idx * 3] = 0.18; nodeColors[idx * 3 + 1] = 0.52; nodeColors[idx * 3 + 2] = 0.35;
            }
            idx++;
        }

        const edgeIndices = new Uint32Array(this.edges.length * 2);
        for (let i = 0; i < this.edges.length; i++) {
            const e = this.edges[i];
            edgeIndices[i * 2] = idToIndex.get(e.source);
            edgeIndices[i * 2 + 1] = idToIndex.get(e.target);
        }

        return {
            nodeCount: this.nodes.size,
            edgeCount: this.edges.length,
            nodePositions,
            nodeColors,
            edgeIndices
        };
    }

    escapeHtml(str) {
        if (!str) return "";
        return String(str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}
