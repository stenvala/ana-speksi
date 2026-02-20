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
        "exception": "#D946EF",     # Magenta - optional/exception (easier to see)
        "external": "#22C55E",      # Green - external elements
    }

    # Create a new directed graph
    dot = Digraph(
        name="ana-speksi-workflow",
        comment="ana-speksi Spec-Driven Development Workflow",
        format="png",
    )

    # Graph attributes for compact appearance with minimal whitespace
    dot.attr(
        rankdir="LR",               # Left to Right (horizontal workflow)
        splines="line",             # Straight lines instead of orthogonal/curved
        nodesep="0.25",             # Minimal node spacing
        ranksep="0.5",              # Minimal rank spacing
        margin="0.05",              # Minimal margins
        pad="0.05",
        overlap="false",
        center="true",
    )
    dot.attr("node", shape="box", style="rounded,filled", fontname="Helvetica", margin="0.08")
    dot.attr("edge", fontname="Helvetica", fontsize="8", labelloc="center", arrowsize="0.8")

    # Ground Truth - full width at top
    dot.node(
        "truth",
        "Ground Truth (ana-speksi/truth/)",
        fillcolor=colors["external"],
        color="#5A4A9B",
        fontcolor="white",
        penwidth="2",
        width="20",
        height="0.5",
        fixedsize="true",
    )

    # Main workflow nodes (all on same rank)
    workflow_nodes = [
        ("new", "/as-new\nCreate Proposal"),
        ("storify", "/as-storify\nFunctional Specs"),
        ("techify", "/as-techify\nResearch + Tech Specs"),
        ("taskify", "/as-taskify\nImplementation Tasks"),
        ("codify", "/as-codify\nWrite Code"),
        ("docufy", "/as-docufy\nArchive"),
    ]

    for node_id, label in workflow_nodes:
        dot.node(
            node_id,
            label,
            fillcolor=colors["workflow"],
            color="#2E5C8A",
            fontcolor="white",
            penwidth="2",
            height="0.7",
        )

    # Exception/Optional nodes (below the main line)
    exception_nodes = [
        ("extend", "/as-extend\nMissing Piece"),
        ("verdict", "/as-final-verdict\nDeferred Work"),
    ]

    for node_id, label in exception_nodes:
        dot.node(
            node_id,
            label,
            fillcolor=colors["exception"],
            color="#A21CAF",
            fontcolor="white",
            penwidth="2",
            height="0.7",
        )

    # Project Skills - full width at bottom
    dot.node(
        "skills",
        "Project Skills (your repo's patterns)",
        fillcolor=colors["external"],
        color="#5A4A9B",
        fontcolor="white",
        penwidth="2",
        width="20",
        height="0.5",
        fixedsize="true",
    )

    # Force Ground Truth on top rank
    with dot.subgraph(name="cluster_rank_0") as rank0:
        rank0.attr(rank="source")
        rank0.node("truth")

    # Force main workflow on same rank
    with dot.subgraph(name="cluster_rank_1") as rank1:
        rank1.attr(rank="same")
        for node_id, _ in workflow_nodes:
            rank1.node(node_id)

    # Force extend and verdict below main line
    with dot.subgraph(name="cluster_rank_2") as rank2:
        rank2.attr(rank="same")
        for node_id, _ in exception_nodes:
            rank2.node(node_id)

    # Force skills on bottom rank
    with dot.subgraph(name="cluster_rank_3") as rank3:
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
            penwidth="2",
            headport="w",
            tailport="e",
        )

    # Optional/Exception edges branching off
    dot.edge("codify", "extend", "gap discovered", color=colors["exception"], penwidth="1.5")
    dot.edge("extend", "codify", "new requirements", color=colors["exception"], penwidth="1.5")
    dot.edge("codify", "verdict", "optional", color=colors["exception"], penwidth="1.5")
    dot.edge("verdict", "docufy", "informs", color=colors["exception"], penwidth="1.5")

    # Integration edges with external elements (solid lines, not dashed)
    dot.edge(
        "truth",
        "new",
        "reads",
        color=colors["external"],
        fontcolor=colors["external"],
        penwidth="1",
        constraint="false",
    )
    dot.edge(
        "techify",
        "skills",
        "identifies",
        color=colors["external"],
        fontcolor=colors["external"],
        penwidth="1",
        constraint="false",
    )
    dot.edge(
        "taskify",
        "skills",
        "assigns",
        color=colors["external"],
        fontcolor=colors["external"],
        penwidth="1",
        constraint="false",
    )
    dot.edge(
        "codify",
        "skills",
        "invokes",
        color=colors["external"],
        fontcolor=colors["external"],
        penwidth="1",
        constraint="false",
    )
    dot.edge(
        "docufy",
        "truth",
        "updates",
        color=colors["external"],
        fontcolor=colors["external"],
        penwidth="1",
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
