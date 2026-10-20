// tests/test_lean_dag_visualizer.mjs
// Unit tests for LeanDagVisualizer and Tufte Proof-Walk Engine
// Strict 7-bit ASCII only (INV-001).

import assert from "node:assert/strict";
import { LeanDagVisualizer } from "./lean_dag_visualizer.js";

console.log("=== Testing LeanDagVisualizer Suite ===");

const sampleGraph = {
    nodes: [
        {
            id: "def:matrix_antisym",
            label: "EulerPacketPiola.matrixAntisym",
            kind: "definition",
            module: "Euler.PacketPiolaAlgebra",
            line: 19,
            statement: "def matrixAntisym (A : Mat3) : Fin 3 -> Real",
            docstring: "Vector antisymmetrization of 3x3 matrices."
        },
        {
            id: "thm:matrixantisym_congruence",
            label: "EulerPacketPiola.matrixAntisym_congruence",
            kind: "theorem",
            module: "Euler.PacketPiolaAlgebra",
            line: 23,
            statement: "theorem matrixAntisym_congruence (F A : Mat3) : matrixAntisym (F.transpose * A * F) = F.adjugate.mulVec (matrixAntisym A)",
            docstring: "Adjugate transformation polynomial identity.",
            milestones: ["Line 25: ext i", "Line 26: fin_cases i", "Line 30: ring"],
            uses: ["def:matrix_antisym"]
        },
        {
            id: "thm:piola_curl",
            label: "EulerPacketPiola.piola_curl",
            kind: "theorem",
            module: "Euler.PacketPiola",
            line: 60,
            statement: "theorem piola_curl : F.symm (curlMatrix ...) = vectorCurl ...",
            docstring: "Genuine curl Piola transformation identity.",
            milestones: ["Line 67: rw [curl_pullbackCovector]", "Line 68: exact ..."],
            uses: ["thm:matrixantisym_congruence"]
        },
        {
            id: "thm:divergence_piola_curl",
            label: "EulerPacketPiola.divergence_piola_curl",
            kind: "theorem",
            module: "Euler.PacketPiola",
            line: 77,
            statement: "theorem divergence_piola_curl : divergence ... = 0",
            docstring: "Exact solenoidal gauge without Biot-Savart convolution.",
            uses: ["thm:piola_curl"]
        }
    ],
    edges: [
        { source: "def:matrix_antisym", target: "thm:matrixantisym_congruence" },
        { source: "thm:matrixantisym_congruence", target: "thm:piola_curl" },
        { source: "thm:piola_curl", target: "thm:divergence_piola_curl" }
    ]
};

// Test 1: Load graph and verify node/edge parsing
{
    const viz = new LeanDagVisualizer();
    viz.loadGraphData(sampleGraph);

    assert.strictEqual(viz.nodes.size, 4, "Loaded 4 nodes");
    assert.strictEqual(viz.edges.length, 3, "Loaded 3 edges");
    assert.strictEqual(viz.layers.length, 4, "Computed 4 topological layers");

    assert.strictEqual(viz.nodes.get("def:matrix_antisym").layer, 0, "Base definition is layer 0");
    assert.strictEqual(viz.nodes.get("thm:matrixantisym_congruence").layer, 1, "Congruence theorem is layer 1");
    assert.strictEqual(viz.nodes.get("thm:piola_curl").layer, 2, "Piola curl is layer 2");
    assert.strictEqual(viz.nodes.get("thm:divergence_piola_curl").layer, 3, "Divergence-free is layer 3");

    console.log("  - Topological Layer Computation: PASS");
}

// Test 2: Verify coordinate layout
{
    const viz = new LeanDagVisualizer({ layerSpacing: 100, nodeSpacing: 50 });
    viz.loadGraphData(sampleGraph);

    for (let l = 0; l < viz.layers.length; l++) {
        for (const nodeId of viz.layers[l]) {
            const node = viz.nodes.get(nodeId);
            assert.strictEqual(node.x, l * 100 + 50, `Node ${nodeId} x-coordinate matches layer`);
            assert(typeof node.y === "number", `Node ${nodeId} has valid y-coordinate`);
        }
    }
    console.log("  - Coordinate Layout: PASS");
}

// Test 3: Tufte proof-walk card generation
{
    const viz = new LeanDagVisualizer();
    viz.loadGraphData(sampleGraph);

    const html = viz.renderTufteProofWalk("thm:matrixantisym_congruence");
    assert(html.includes("tufte-proof-card"), "Generates tufte-proof-card element");
    assert(html.includes("EulerPacketPiola.matrixAntisym_congruence"), "Includes theorem title");
    assert(html.includes("Layer 1"), "Displays layer depth");
    assert(html.includes("Proof Strategy Milestones:"), "Displays milestones header");
    assert(html.includes("Line 30: ring"), "Includes milestone step");
    assert(html.includes("def:matrix_antisym"), "Includes premise dependency tag");
    assert(html.includes("thm:piola_curl"), "Includes dependent theorem tag");

    console.log("  - Tufte Proof-Walk Rendering: PASS");
}

// Test 4: SVG generation
{
    const viz = new LeanDagVisualizer();
    viz.loadGraphData(sampleGraph);

    const svg = viz.exportSvg();
    assert(svg.startsWith("<svg"), "Produces valid SVG root element");
    assert(svg.includes("<circle"), "Includes SVG node circles");
    assert(svg.includes("<line"), "Includes SVG edge lines");
    assert(svg.includes("marker-end=\"url(#arrow)\""), "Includes arrowhead markers");

    console.log("  - SVG Graph Export: PASS");
}

// Test 5: WebGL buffers
{
    const viz = new LeanDagVisualizer();
    viz.loadGraphData(sampleGraph);

    const buffer = viz.toWebGLBuffer();
    assert.strictEqual(buffer.nodeCount, 4, "Buffer reports 4 nodes");
    assert.strictEqual(buffer.edgeCount, 3, "Buffer reports 3 edges");
    assert.strictEqual(buffer.nodePositions.length, 8, "Float32Array has 8 floats for 4 (x,y) pairs");
    assert.strictEqual(buffer.edgeIndices.length, 6, "Uint32Array has 6 indices for 3 edges");

    console.log("  - WebGL Instancing Buffer: PASS");
}

console.log("=== All LeanDagVisualizer Tests Passed ===");
