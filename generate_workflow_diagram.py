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
        "exception": "#F5A623",     # Orange - optional/exception
        "external": "#22C55E",      # Green - external elements
    }

    # Create a new directed graph
    dot = Digraph(
        name="ana-speksi-workflow",
        comment="ana-speksi Spec-Driven Development Workflow",
        format="png",
    )

    # Graph attributes for professional appearance
    dot.attr(
        rankdir="LR",               # Left to Right (horizontal workflow)
        splines="ortho",            # Orthogonal edges for cleaner lines
        nodesep="0.6",
        ranksep="1.2",
    )
    dot.attr("node", shape="box", style="rounded,filled", fontname="Helvetica")
    dot.attr("edge", fontname="Helvetica", fontsize="10")

    # External elements (Ground Truth, Project Skills) - wider boxes
    dot.node(
        "truth",
        "Ground Truth (ana-speksi/truth/)",
        fillcolor=colors["external"],
        color="#5A4A9B",
        fontcolor="white",
        penwidth="2",
        width="3",
        height="0.6",
    )
    dot.node(
        "skills",
        "Project Skills (your repo's patterns)",
        fillcolor=colors["external"],
        color="#5A4A9B",
        fontcolor="white",
        penwidth="2",
        width="3",
        height="0.6",
    )

    # Main workflow nodes
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
        )

    # Exception/Optional nodes
    exception_nodes = [
        ("extend", "/as-extend\nMissing Piece"),
        ("verdict", "/as-final-verdict\nDeferred Work"),
    ]

    for node_id, label in exception_nodes:
        dot.node(
            node_id,
            label,
            fillcolor=colors["exception"],
            color="#C17E1D",
            fontcolor="white",
            penwidth="2",
        )

    # Create subgraph for vertical grouping (Ground Truth on top)
    with dot.subgraph(name="cluster_top") as top:
        top.attr(style="invis")
        top.node("truth")

    # Create subgraph for main workflow (middle)
    with dot.subgraph(name="cluster_workflow") as workflow:
        workflow.attr(style="invis")

        # Main workflow edges (accept gates) - horizontal flow
        workflow_edges = [
            ("new", "storify", "accept"),
            ("storify", "techify", "accept"),
            ("techify", "taskify", "accept"),
            ("taskify", "codify", "accept"),
        ]

        for source, target, label in workflow_edges:
            dot.edge(source, target, label, color=colors["workflow"], penwidth="2")

        # Optional/Exception edges branching up/down from codify
        dot.edge("codify", "extend", "gap discovered", color=colors["exception"], penwidth="2")
        dot.edge("extend", "codify", "new requirements", color=colors["exception"], penwidth="2")
        dot.edge("codify", "verdict", "optional", color=colors["exception"], penwidth="2")

        # Final archival edges
        dot.edge("verdict", "docufy", color=colors["workflow"], penwidth="2")
        dot.edge("codify", "docufy", color=colors["workflow"], penwidth="2")

    # Create subgraph for bottom (Project Skills)
    with dot.subgraph(name="cluster_bottom") as bottom:
        bottom.attr(style="invis")
        bottom.node("skills")

    # Integration edges with external elements
    dot.edge(
        "truth",
        "new",
        "reads",
        style="dashed",
        color=colors["external"],
        fontcolor=colors["external"],
        constraint="false",
    )
    dot.edge(
        "truth",
        "techify",
        "reads",
        style="dashed",
        color=colors["external"],
        fontcolor=colors["external"],
        constraint="false",
    )
    dot.edge(
        "techify",
        "skills",
        "identifies",
        style="dashed",
        color=colors["external"],
        fontcolor=colors["external"],
        constraint="false",
    )
    dot.edge(
        "taskify",
        "skills",
        "assigns",
        style="dashed",
        color=colors["external"],
        fontcolor=colors["external"],
        constraint="false",
    )
    dot.edge(
        "codify",
        "skills",
        "AI invokes",
        style="dashed",
        color=colors["external"],
        fontcolor=colors["external"],
        constraint="false",
    )
    dot.edge(
        "verdict",
        "docufy",
        "informs",
        style="dashed",
        color=colors["exception"],
        fontcolor=colors["exception"],
    )
    dot.edge(
        "docufy",
        "truth",
        "updates",
        style="dashed",
        color=colors["external"],
        fontcolor=colors["external"],
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
