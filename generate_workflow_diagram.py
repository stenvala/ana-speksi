#!/usr/bin/env python3
"""
Generate a table-style workflow diagram for the ana-speksi framework using matplotlib.
Creates a grid-based layout matching the README workflow.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def create_workflow_diagram(output_path="workflow_diagram"):
    """
    Create and render the ana-speksi workflow diagram as a table.

    Args:
        output_path: Path and filename without extension (default: workflow_diagram.png)
    """

    # Colors
    colors = {
        "workflow": "#4A90E2",      # Blue
        "start": "#DD9D2F",         # Amber
        "exception": "#D946EF",     # Magenta
        "external": "#257403",      # Dark green
        "white": "#FFFFFF",
    }

    # Create figure and axis with reduced height due to fewer rows
    fig, ax = plt.subplots(figsize=(22, 8.5))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis("off")

    # Helper function to draw box
    def draw_box(ax, x, y, width, height, text, fillcolor, textcolor="white", fontsize=11, style="round"):
        box = FancyBboxPatch(
            (x - width / 2, y - height / 2),
            width,
            height,
            boxstyle="round,pad=0.1" if style == "round" else "square,pad=0.05",
            linewidth=2,
            edgecolor=fillcolor,
            facecolor=fillcolor,
            zorder=2,
        )
        ax.add_patch(box)
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=fontsize,
            color=textcolor,
            weight="bold",
            zorder=3,
        )

    # Helper function to draw arrow
    def draw_arrow(ax, x1, y1, x2, y2, label="", color="black", linestyle="solid", width=2.5):
        arrow = FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="->",
            mutation_scale=22,
            linewidth=width,
            color=color,
            linestyle=linestyle,
            zorder=1,
        )
        ax.add_patch(arrow)
        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            offset_y = 0.16 if linestyle == "solid" else 0.1
            ax.text(
                mid_x,
                mid_y + offset_y,
                label,
                ha="center",
                fontsize=9,
                color=color,
                weight="bold",
                zorder=3,
            )

    # ===== ROW 0 (y=4.5): GROUND TRUTH =====
    draw_box(
        ax,
        5.5,
        4.5,
        11,
        0.7,
        "Ground Truth (ana-speksi/truth/)",
        colors["external"],
        fontsize=13,
    )

    # ===== ROW 1 (y=3.2): EXCEPTION BOXES =====
    draw_box(ax, 2.0, 3.2, 1.6, 0.75, "as-extend\nMissing Piece", colors["exception"], fontsize=11)
    draw_box(
        ax, 9.8, 3.2, 1.8, 0.75, "as-final-verdict\nDeferred Work", colors["exception"], fontsize=11
    )

    # ===== ROW 2 (y=1.5): WORKFLOW BOXES WITH ARROWS =====
    workflow_boxes = [
        (0.8, "as-new\nCreate Proposal", colors["start"]),
        (2.2, "as-storify\nFunctional Specs", colors["workflow"]),
        (3.8, "as-techify\nResearch + Tech", colors["workflow"]),
        (5.5, "as-taskify\nImplementation", colors["workflow"]),
        (7.2, "as-codify\nWrite Code", colors["workflow"]),
        (9.0, "as-docufy\nArchive", colors["workflow"]),
    ]

    for x, label, color in workflow_boxes:
        draw_box(ax, x, 1.5, 1.1, 0.75, label, color, fontsize=11)

    # Draw horizontal arrows between workflow boxes
    arrow_positions = [
        (1.35, 1.5, 1.85, 1.5, "accept"),
        (2.75, 1.5, 3.25, 1.5, "accept"),
        (4.35, 1.5, 5.05, 1.5, "accept"),
        (5.95, 1.5, 6.7, 1.5, "accept"),
        (7.7, 1.5, 8.4, 1.5, "accept"),
    ]

    for x1, y1, x2, y2, label in arrow_positions:
        draw_arrow(ax, x1, y1, x2, y2, label, colors["workflow"], width=2.5)

    # ===== ROW 3 (y=0.35): SKILLS =====
    draw_box(ax, 5.5, 0.35, 11, 0.7, "Project Skills (your repo's patterns)", colors["external"], fontsize=13)

    # ===== VERTICAL ARROWS: Ground Truth connections =====
    # NEW reads from truth
    draw_arrow(ax, 4.8, 4.15, 0.8, 2.15, "reads", colors["external"], width=1.5)

    # STORIFY reads from truth
    draw_arrow(ax, 5.2, 4.15, 2.2, 2.15, "reads", colors["external"], width=1.5)

    # TECHIFY reads from truth
    draw_arrow(ax, 5.5, 4.15, 3.8, 2.15, "reads", colors["external"], width=1.5)

    # ===== VERTICAL ARROWS: Workflow to Skills =====
    # TECHIFY identifies skills
    draw_arrow(ax, 4.1, 1.1, 5.0, 0.75, "identifies", colors["external"], width=1.5)

    # TASKIFY assigns skills
    draw_arrow(ax, 5.5, 1.1, 5.5, 0.75, "assigns", colors["external"], width=1.5)

    # CODIFY invokes skills
    draw_arrow(ax, 7.2, 1.1, 6.2, 0.75, "invokes", colors["external"], width=1.5)

    # DOCUFY updates truth
    draw_arrow(ax, 8.8, 2.15, 8.8, 4.15, "updates", colors["external"], width=1.5)

    # ===== EXCEPTION FLOW =====
    # CODIFY to EXTEND (gap discovered)
    draw_arrow(ax, 6.7, 1.85, 2.5, 2.85, "gap discovered", colors["exception"], "dashed", width=2)

    # EXTEND back to CODIFY (new requirements)
    draw_arrow(ax, 2.5, 3.55, 6.7, 1.85, "new requirements", colors["exception"], "dashed", width=2)

    # CODIFY to VERDICT (optional)
    draw_arrow(ax, 7.6, 1.85, 9.3, 2.85, "optional", colors["exception"], "dashed", width=2)

    # VERDICT to DOCUFY (informs)
    draw_arrow(ax, 9.3, 3.55, 9.0, 2.2, "informs", colors["exception"], "dashed", width=2)

    # Save figure
    plt.tight_layout()
    plt.savefig(f"{output_path}.png", dpi=150, bbox_inches="tight", facecolor="white")
    print(f"✅ Workflow diagram saved to: {output_path}.png")

    import os
    file_size = os.path.getsize(f"{output_path}.png") / 1024
    print(f"   File size: {file_size:.1f} KB")
    print(f"\nUpdates applied:")
    print(f"  ✓ Dark green (#257403) for Ground Truth and Skills")
    print(f"  ✓ Increased font sizes (11-13pt for boxes)")
    print(f"  ✓ Reduced vertical whitespace (3 rows instead of 7)")
    print(f"  ✓ All relationships from README.md integrated:")
    print(f"    - NEW, STORIFY, TECHIFY read from Ground Truth")
    print(f"    - TECHIFY identifies skills, TASKIFY assigns, CODIFY invokes")
    print(f"    - DOCUFY updates Ground Truth")
    print(f"    - CODIFY ↔ EXTEND (gap/new requirements)")
    print(f"    - CODIFY → VERDICT → DOCUFY (optional)")
    print(f"  ✓ Arrow widths maintained (2.5pt horizontal, 1.5pt vertical)")


if __name__ == "__main__":
    create_workflow_diagram()
