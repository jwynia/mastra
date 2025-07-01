import plotly.graph_objects as go
import plotly.express as px
import json

# Data from the provided JSON
data = {
  "nodes": [
    {"id": "af_file", "label": ".af File\n(JSON)", "type": "input", "x": 50, "y": 200},
    {"id": "validator", "label": "Zod Schema\nValidator", "type": "process", "x": 200, "y": 200},
    {"id": "parser", "label": "AF Parser", "type": "process", "x": 350, "y": 200},
    {"id": "memory_converter", "label": "Memory\nConverter", "type": "process", "x": 500, "y": 100},
    {"id": "tool_converter", "label": "Tool\nConverter", "type": "process", "x": 500, "y": 200},
    {"id": "config_converter", "label": "Config\nConverter", "type": "process", "x": 500, "y": 300},
    {"id": "agent_factory", "label": "Mastra Agent\nFactory", "type": "process", "x": 650, "y": 200},
    {"id": "mastra_agent", "label": "Mastra Agent\nInstance", "type": "output", "x": 800, "y": 200},
    {"id": "export_serializer", "label": "Export\nSerializer", "type": "process", "x": 650, "y": 350},
    {"id": "export_af", "label": "Exported\n.af File", "type": "output", "x": 800, "y": 350}
  ],
  "edges": [
    {"from": "af_file", "to": "validator", "label": "Parse JSON"},
    {"from": "validator", "to": "parser", "label": "Valid .af"},
    {"from": "parser", "to": "memory_converter", "label": "Core Memory +\nMessages"},
    {"from": "parser", "to": "tool_converter", "label": "Tools +\nTool Rules"},
    {"from": "parser", "to": "config_converter", "label": "LLM Config +\nEmbedding Config"},
    {"from": "memory_converter", "to": "agent_factory", "label": "Memory Object"},
    {"from": "tool_converter", "to": "agent_factory", "label": "Tools Array"},
    {"from": "config_converter", "to": "agent_factory", "label": "Model Config"},
    {"from": "agent_factory", "to": "mastra_agent", "label": "Create Agent"},
    {"from": "mastra_agent", "to": "export_serializer", "label": "Export Request"},
    {"from": "export_serializer", "to": "export_af", "label": "Serialize to .af"}
  ]
}

# Create a mapping for node positions
node_positions = {node["id"]: (node["x"], node["y"]) for node in data["nodes"]}

# Color mapping for node types
type_colors = {
    "input": "#1FB8CD",      # Strong cyan
    "process": "#FFC185",    # Light orange  
    "output": "#5D878F"      # Cyan
}

fig = go.Figure()

# Add edges (lines) first so they appear behind nodes
for edge in data["edges"]:
    from_pos = node_positions[edge["from"]]
    to_pos = node_positions[edge["to"]]
    
    # Add line
    fig.add_trace(go.Scatter(
        x=[from_pos[0], to_pos[0]],
        y=[from_pos[1], to_pos[1]],
        mode='lines',
        line=dict(color='#13343B', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Add arrow head
    # Calculate arrow position (90% along the line)
    arrow_x = from_pos[0] + 0.9 * (to_pos[0] - from_pos[0])
    arrow_y = from_pos[1] + 0.9 * (to_pos[1] - from_pos[1])
    
    fig.add_trace(go.Scatter(
        x=[arrow_x],
        y=[arrow_y],
        mode='markers',
        marker=dict(
            symbol='triangle-right',
            size=8,
            color='#13343B'
        ),
        showlegend=False,
        hoverinfo='skip'
    ))

# Add nodes
for node in data["nodes"]:
    fig.add_trace(go.Scatter(
        x=[node["x"]],
        y=[node["y"]],
        mode='markers+text',
        marker=dict(
            size=60,
            color=type_colors[node["type"]],
            line=dict(width=2, color='#13343B')
        ),
        text=node["label"],
        textposition="middle center",
        textfont=dict(size=10, color='black'),
        name=node["type"].title(),
        showlegend=True,
        hoverinfo='skip'
    ))

# Remove duplicate legend entries
seen_types = set()
for trace in fig.data:
    if hasattr(trace, 'name') and trace.name:
        if trace.name in seen_types:
            trace.showlegend = False
        else:
            seen_types.add(trace.name)

# Update layout
fig.update_layout(
    title="Mastra .af Agent Architecture",
    xaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[-20, 870]
    ),
    yaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[50, 400]
    ),
    plot_bgcolor='white',
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.05,
        xanchor='center',
        x=0.5
    )
)

# Save the chart
fig.write_image("mastra_af_architecture.png")