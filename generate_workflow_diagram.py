#!/usr/bin/env python3
"""
Generate a table-style workflow diagram for the ana-speksi framework using matplotlib.
Creates a grid-based layout matching the README workflow.
Create image to run uv run generate_workflow_diagram.py
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import math


def adjust_arrow_endpoints(x1, y1, x2, y2, gap=0.05):
    """
    Adjust arrow endpoints to add a gap from boxes.

    Args:
        x1, y1: Start point
        x2, y2: End point
        gap: Gap distance to add

    Returns:
        Tuple of (adjusted_x1, adjusted_y1, adjusted_x2, adjusted_y2)
    """
    # Calculate direction vector
    dx = x2 - x1
    dy = y2 - y1

    # Calculate distance
    distance = math.sqrt(dx**2 + dy**2)

    if distance == 0:
        return x1, y1, x2, y2

    # Normalize direction vector
    norm_dx = dx / distance
    norm_dy = dy / distance

    # Move points inward by gap distance
    new_x1 = x1 + norm_dx * gap
    new_y1 = y1 + norm_dy * gap
    new_x2 = x2 - norm_dx * gap
    new_y2 = y2 - norm_dy * gap

    return new_x1, new_y1, new_x2, new_y2


def draw_orthogonal_arrow(
    ax, x1, y1, x2, y2, label="", color="black", linestyle="solid", width=3.5, gap=0.05
):
    """
    Draw a straight vertical arrow from (x1, y1) to (x2, y2).
    x2 should equal x1 for straight vertical lines.

    Args:
        ax: matplotlib axis
        x1, y1: Start point (center of source box)
        x2, y2: End point (must have x2 == x1 for vertical line)
        label: Label text for the arrow
        color: Arrow color
        linestyle: Line style (solid, dashed, etc.)
        width: Line width
        gap: Gap from box edge
    """
    # Adjust end point vertically
    if y2 > y1:  # going up
        adj_y2 = y2 - gap
    else:  # going down
        adj_y2 = y2 + gap

    # Adjust start point vertically
    if y1 < y2:  # going up
        adj_y1 = y1 + gap
    else:  # going down
        adj_y1 = y1 - gap

    # Draw straight vertical arrow with arrowhead
    arrow = FancyArrowPatch(
        (x1, adj_y1),
        (x1, adj_y2),
        arrowstyle="->",
        mutation_scale=112,
        linewidth=width,
        color=color,
        linestyle=linestyle,
        zorder=1,
    )
    ax.add_patch(arrow)

    # Add label at the center of the path
    if label:
        label_x = x1
        label_y = (y1 + y2) / 2
        offset_x = 0.15
        ax.text(
            label_x + offset_x,
            label_y,
            label,
            ha="left",
            fontsize=27,
            color=color,
            weight="bold",
            zorder=3,
        )


def create_workflow_diagram(output_path="workflow_diagram"):
    """
    Create and render the ana-speksi workflow diagram as a table.

    Args:
        output_path: Path and filename without extension (default: workflow_diagram.png)
    """

    # Colors
    colors = {
        "workflow": "#4A90E2",  # Blue
        "start": "#DD9D2F",  # Amber
        "exception": "#D946EF",  # Magenta
        "external": "#257403",  # Dark green
        "white": "#FFFFFF",
    }

    # Create figure and axis with larger size for bigger text
    fig, ax = plt.subplots(figsize=(40, 16))
    ax.set_xlim(-0.5, 11.5)
    ax.set_ylim(-0.6, 5)
    ax.axis("off")

    # Helper function to draw box
    def draw_box(
        ax,
        x,
        y,
        width,
        height,
        text,
        fillcolor,
        textcolor="white",
        fontsize=11,
        style="round",
    ):
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

        # Split text into command (first line) and description (second line)
        lines = text.split("\n")
        if len(lines) == 2:
            command, description = lines
            # Draw command in italic at top
            ax.text(
                x,
                y + fontsize * 0.002,
                command,
                ha="center",
                va="bottom",
                fontsize=fontsize,
                color=textcolor,
                weight="bold",
                zorder=3,
            )
            # Draw description in normal style at bottom (tightly below)
            ax.text(
                x,
                y - fontsize * 0.002,
                description,
                ha="center",
                va="top",
                fontsize=fontsize,
                color=textcolor,
                weight="bold",
                fontstyle="normal",
                zorder=3,
            )
        else:
            # Fallback for single-line text
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
    def draw_arrow(
        ax,
        x1,
        y1,
        x2,
        y2,
        label="",
        color="black",
        linestyle="solid",
        width=3.5,
        offset_y=0.2,
        offset_x=0,
    ):
        arrow = FancyArrowPatch(
            (x1, y1),
            (x2, y2),
            arrowstyle="->",
            mutation_scale=112,
            linewidth=width,
            color=color,
            linestyle=linestyle,
            zorder=1,
        )
        ax.add_patch(arrow)
        if label:
            mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
            ax.text(
                mid_x + offset_x,
                mid_y + offset_y,
                label,
                ha="center",
                fontsize=27,
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
        "Functional and Technical Documentation",
        colors["external"],
        fontsize=42,
        style="round",
    )

    # ===== ROW 1 (y=3.2): EXCEPTION BOXES =====
    draw_box(
        ax,
        6.5,
        3.2,
        1.6,
        0.75,
        "extend\nMissing Piece",
        colors["exception"],
        fontsize=33,
    )
    draw_box(
        ax,
        8.5,
        3.2,
        1.8,
        0.75,
        "final-verdict\nDeferred Work",
        colors["exception"],
        fontsize=33,
    )

    # ===== ROW 2 (y=1.5): WORKFLOW BOXES WITH ARROWS =====
    # Distribute 6 boxes and 5 gaps evenly across width 11
    # Each box and gap is 1 unit wide
    workflow_boxes = [
        (0.5, "new\nCreate Proposal", colors["start"]),
        (2.5, "storify\nFunctional\nSpecs", colors["workflow"]),
        (4.5, "techify\nResearch +\nTech", colors["workflow"]),
        (6.5, "taskify\nImplemen-\ntation", colors["workflow"]),
        (8.5, "codify\nWrite Code", colors["workflow"]),
        (10.5, "docufy\nArchive", colors["workflow"]),
    ]

    for x, label, color in workflow_boxes:
        draw_box(ax, x, 1.5, 1.0, 0.75, label, color, fontsize=28)

    # ===== JIRA SYNC BOXES =====
    # Add Jira sync boxes under new, storify, and docufy
    jira_boxes = [
        (0.5, "Jira look"),  # Under new
        (2.5, "Jira create"),  # Under storify
        (10.5, "Jira update"),  # Under docufy
    ]

    jira_height = 0.75 * 0.35  # 35% of the box above
    jira_y = (
        1.5 - 0.75 / 2 - jira_height / 2 - 0.1
    )  # Directly under the box above, moved down

    for x, label in jira_boxes:
        draw_box(
            ax,
            x,
            jira_y,
            1.0,
            jira_height,
            label,
            "#000000",
            textcolor="white",
            fontsize=28,
        )

    # Draw horizontal arrows between workflow boxes (centered in each gap)
    arrow_positions = [
        (1.15, 1.5, 1.9, 1.5, "accept"),
        (3.15, 1.5, 3.9, 1.5, "accept"),
        (5.15, 1.5, 5.9, 1.5, "accept"),
        (7.15, 1.5, 7.9, 1.5, "accept"),
        (9.15, 1.5, 9.9, 1.5, "accept"),
    ]

    for x1, y1, x2, y2, label in arrow_positions:
        adj_x1, adj_y1, adj_x2, adj_y2 = adjust_arrow_endpoints(x1, y1, x2, y2)
        draw_arrow(
            ax, adj_x1, adj_y1, adj_x2, adj_y2, label, colors["workflow"], width=8.0
        )

    # ===== ROW 3 (y=-0.15): SKILLS =====
    draw_box(
        ax,
        5.5,
        -0.15,
        11,
        0.7,
        "Agent's skills",
        colors["external"],
        fontsize=42,
        style="round",
    )

    # ===== VERTICAL ARROWS: Ground Truth connections =====
    # NEW reads from truth
    draw_orthogonal_arrow(ax, 0.5, 2, 0.5, 4.05, "reads", colors["external"], width=8.0)

    # STORIFY reads from truth
    draw_orthogonal_arrow(ax, 2.5, 2, 2.5, 4.05, "reads", colors["external"], width=8.0)

    # TECHIFY reads from truth
    draw_orthogonal_arrow(ax, 4.5, 2, 4.5, 4.05, "reads", colors["external"], width=8.0)

    # ===== VERTICAL ARROWS: Workflow to Skills =====
    # TECHIFY identifies skills
    draw_orthogonal_arrow(
        ax, 4.5, 1, 4.5, 0.3, "identifies", colors["workflow"], width=8.0
    )

    # TASKIFY assigns skills
    draw_orthogonal_arrow(
        ax, 6.5, 1, 6.5, 0.3, "assigns", colors["workflow"], width=8.0
    )

    # CODIFY invokes skills
    draw_orthogonal_arrow(
        ax, 8.5, 1, 8.5, 0.3, "invokes", colors["workflow"], width=8.0
    )

    # DOCUFY updates truth
    draw_orthogonal_arrow(
        ax, 10.5, 2, 10.5, 4.05, "updates", colors["external"], width=8.0
    )

    # ===== EXCEPTION FLOW =====

    # CODIFY to EXTEND (diagonal with gap label)
    draw_arrow(
        ax,
        8,
        2.05,
        7.3,
        2.7,
        "gap",
        colors["exception"],
        width=8.0,
        offset_y=0,
        offset_x=0.3,
    )

    # CODIFY to FINAL-VERDICT (vertical with exclude label)
    draw_orthogonal_arrow(
        ax, 8.5, 2, 8.5, 2.75, "exclude", colors["exception"], width=8.0
    )

    # DOCUFY to FINAL-VERDICT (diagonal with consider label)
    draw_arrow(
        ax,
        10,
        2.05,
        9.3,
        2.7,
        "consider",
        colors["exception"],
        width=8.0,
        offset_y=0,
        offset_x=0.35,
    )

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
