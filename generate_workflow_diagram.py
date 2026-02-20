#!/usr/bin/env python3
"""
Generate a professional workflow diagram for the ana-speksi framework.
Uses Graphviz to create a compact, visually appealing PNG suitable for LinkedIn.
"""

from graphviz import Digraph


def create_workflow_diagram(output_path="workflow_diagram"):
    """
    Create and render the ana-speksi workflow diagram.

    Args:
        output_path: Path and filename without extension (default: workflow_diagram.png)
    """

    # Color scheme matching the mermaid diagram
    colors = {
        "workflow": "#4A90E2",      # Blue - normal workflow
        "start": "#F59E0B",         # Amber - starting point
        "exception": "#D946EF",     # Magenta - optional/exception (easier to see)
        "external": "#8B6F47",      # Brown - external elements
    }

    # Create a new directed graph
    dot = Digraph(
        name="ana-speksi-workflow",
        comment="ana-speksi Spec-Driven Development Workflow",
        format="png",
    )

    # Graph attributes for professional appearance with improved spacing
    dot.attr(
        rankdir="LR",               # Left to Right (horizontal workflow)
        splines="line",             # Straight lines instead of orthogonal/curved
        nodesep="1.3",              # Spacing to span full width of truth box
        ranksep="0.5",              # Compact vertical spacing
        margin="0.05,0.1",          # Minimal left margin, normal top/bottom
        pad="0.1",
        overlap="false",
        center="false",
    )
    dot.attr("node", shape="box", style="rounded,filled", fontname="Helvetica", margin="0.15")
    dot.attr("edge", fontname="Helvetica", fontsize="11", labelloc="center", arrowsize="1.2")

    # Ground Truth - full width at top
    dot.node(
        "truth",
        "Ground Truth (ana-speksi/truth/)",
        fillcolor=colors["external"],
        color="#654321",
        fontcolor="white",
        fontsize="12",
        penwidth="2",
        width="20",
        height="0.65",
        fixedsize="true",
    )

    # Main workflow nodes (all on same rank)
    workflow_nodes = [
        ("new", "as-new\nCreate Proposal"),
        ("storify", "as-storify\nFunctional Specs"),
        ("techify", "as-techify\nResearch + Tech Specs"),
        ("taskify", "as-taskify\nImplementation Tasks"),
        ("codify", "as-codify\nWrite Code"),
        ("docufy", "as-docufy\nArchive"),
    ]

    for i, (node_id, label) in enumerate(workflow_nodes):
        # Use amber color for the starting point (as-new)
        fill_color = colors["start"] if node_id == "new" else colors["workflow"]
        border_color = "#D97706" if node_id == "new" else "#1E40AF"

        dot.node(
            node_id,
            label,
            fillcolor=fill_color,
            color=border_color,
            fontcolor="white",
            fontsize="11",
            penwidth="2",
            width="1.8",
            height="0.85",
            fixedsize="true",
        )

    # Exception/Optional nodes (side by side)
    exception_nodes = [
        ("extend", "as-extend\nMissing Piece"),
        ("verdict", "as-final-verdict\nDeferred Work"),
    ]

    for node_id, label in exception_nodes:
        dot.node(
            node_id,
            label,
            fillcolor=colors["exception"],
            color="#9D174D",
            fontcolor="white",
            fontsize="10",
            penwidth="2",
            width="1.8",
            height="0.80",
            fixedsize="true",
        )

    # Project Skills - full width at bottom
    dot.node(
        "skills",
        "Project Skills (your repo's patterns)",
        fillcolor=colors["external"],
        color="#654321",
        fontcolor="white",
        fontsize="12",
        penwidth="2",
        width="20",
        height="0.65",
        fixedsize="true",
    )

    # Force Ground Truth on top rank
    with dot.subgraph(name="rank_0") as rank0:
        rank0.attr(rank="source")
        rank0.node("truth")

    # Force main workflow on same rank
    with dot.subgraph(name="rank_1") as rank1:
        rank1.attr(rank="same")
        for node_id, _ in workflow_nodes:
            rank1.node(node_id)

    # Force extend and verdict side by side on same rank
    with dot.subgraph(name="rank_2") as rank2:
        rank2.attr(rank="same")
        for node_id, _ in exception_nodes:
            rank2.node(node_id)

    # Force skills on bottom rank
    with dot.subgraph(name="rank_3") as rank3:
        rank3.attr(rank="sink")
        rank3.node("skills")

    # Main workflow edges (accept gates) - horizontal flow
    workflow_edges = [
        ("new", "storify", "accept"),
        ("storify", "techify", "accept"),
        ("techify", "taskify", "accept"),
        ("taskify", "codify", "accept"),
        ("codify", "docufy", "accept"),
    ]

    for source, target, label in workflow_edges:
        dot.edge(
            source,
            target,
            label,
            color=colors["workflow"],
            penwidth="2.5",
            headport="w",
            tailport="e",
        )

    # Optional/Exception edges branching off (dashed for distinction)
    dot.edge("codify", "extend", "gap discovered", color=colors["exception"], penwidth="2", style="dashed")
    dot.edge("extend", "codify", "new requirements", color=colors["exception"], penwidth="2", style="dashed")
    dot.edge("codify", "verdict", "optional", color=colors["exception"], penwidth="2", style="dashed")
    dot.edge("verdict", "docufy", "informs", color=colors["exception"], penwidth="2", style="dashed")

    # Integration edges with external elements (solid lines, subtle but clear)
    dot.edge(
        "truth",
        "new",
        "reads",
        color=colors["external"],
        fontcolor=colors["external"],
        penwidth="1.5",
        constraint="false",
    )
    dot.edge(
        "techify",
        "skills",
        "identifies",
        color=colors["external"],
        fontcolor=colors["external"],
        penwidth="1.5",
        constraint="false",
    )
    dot.edge(
        "taskify",
        "skills",
        "assigns",
        color=colors["external"],
        fontcolor=colors["external"],
        penwidth="1.5",
        constraint="false",
    )
    dot.edge(
        "codify",
        "skills",
        "invokes",
        color=colors["external"],
        fontcolor=colors["external"],
        penwidth="1.5",
        constraint="false",
    )
    dot.edge(
        "docufy",
        "truth",
        "updates",
        color=colors["external"],
        fontcolor=colors["external"],
        penwidth="1.5",
        constraint="false",
    )

    # Render the graph
    output_file = dot.render(output_path, cleanup=True)
    print(f"✅ Workflow diagram saved to: {output_file}")
    print(f"   File size: {__import__('os').path.getsize(output_file) / 1024:.1f} KB")
    print(f"\nColor legend:")
    print(f"  🔵 Blue   = Normal workflow steps")
    print(f"  🟠 Orange = Optional/exception steps (as-extend, as-final-verdict)")
    print(f"  🟣 Purple = External elements (Ground Truth, Project Skills)")


if __name__ == "__main__":
    create_workflow_diagram()
