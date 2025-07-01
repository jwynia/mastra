import plotly.graph_objects as go
import plotly.io as pio

# Define the tree structure with coordinates
nodes = {
    'AgentSchema': {'x': 0, 'y': 5, 'level': 0},
    
    # Level 1 - Main Categories  
    'Core Fields': {'x': -3, 'y': 4, 'level': 1},
    'Configuration': {'x': -1, 'y': 4, 'level': 1},
    'Memory & Msgs': {'x': 1, 'y': 4, 'level': 1},
    'Tooling': {'x': 3, 'y': 4, 'level': 1},
    'Metadata': {'x': 5, 'y': 4, 'level': 1},
    
    # Level 2 - Core Fields
    'agent_type': {'x': -4, 'y': 3, 'level': 2},
    'name': {'x': -3.5, 'y': 3, 'level': 2},
    'system': {'x': -2.5, 'y': 3, 'level': 2},
    'version': {'x': -2, 'y': 3, 'level': 2},
    
    # Level 2 - Configuration
    'llm_config': {'x': -1.3, 'y': 3, 'level': 2},
    'embed_config': {'x': -0.7, 'y': 3, 'level': 2},
    
    # Level 2 - Memory & Messages
    'core_memory': {'x': 0.5, 'y': 3, 'level': 2},
    'messages': {'x': 1, 'y': 3, 'level': 2},
    'msg_indices': {'x': 1.5, 'y': 3, 'level': 2},
    
    # Level 2 - Tooling
    'tools': {'x': 2.5, 'y': 3, 'level': 2},
    'tool_rules': {'x': 3, 'y': 3, 'level': 2},
    'tool_env_vars': {'x': 3.5, 'y': 3, 'level': 2},
    
    # Level 2 - Metadata
    'tags': {'x': 4.5, 'y': 3, 'level': 2},
    'metadata_': {'x': 5, 'y': 3, 'level': 2},
    'created_at': {'x': 5.5, 'y': 3, 'level': 2},
    'updated_at': {'x': 6, 'y': 3, 'level': 2},
}

# Define connections (parent -> children)
connections = [
    ('AgentSchema', 'Core Fields'),
    ('AgentSchema', 'Configuration'),
    ('AgentSchema', 'Memory & Msgs'),
    ('AgentSchema', 'Tooling'),
    ('AgentSchema', 'Metadata'),
    
    ('Core Fields', 'agent_type'),
    ('Core Fields', 'name'),
    ('Core Fields', 'system'),
    ('Core Fields', 'version'),
    
    ('Configuration', 'llm_config'),
    ('Configuration', 'embed_config'),
    
    ('Memory & Msgs', 'core_memory'),
    ('Memory & Msgs', 'messages'),
    ('Memory & Msgs', 'msg_indices'),
    
    ('Tooling', 'tools'),
    ('Tooling', 'tool_rules'),
    ('Tooling', 'tool_env_vars'),
    
    ('Metadata', 'tags'),
    ('Metadata', 'metadata_'),
    ('Metadata', 'created_at'),
    ('Metadata', 'updated_at'),
]

# Color mapping for levels
colors = ['#1FB8CD', '#FFC185', '#ECEBD5']

fig = go.Figure()

# Add connecting lines
for parent, child in connections:
    fig.add_trace(go.Scatter(
        x=[nodes[parent]['x'], nodes[child]['x']],
        y=[nodes[parent]['y'], nodes[child]['y']],
        mode='lines',
        line=dict(color='#5D878F', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))

# Add nodes by level
for level in range(3):
    level_nodes = [name for name, data in nodes.items() if data['level'] == level]
    if level_nodes:
        fig.add_trace(go.Scatter(
            x=[nodes[name]['x'] for name in level_nodes],
            y=[nodes[name]['y'] for name in level_nodes],
            mode='markers+text',
            marker=dict(
                size=[20 if level == 0 else 15 if level == 1 else 12][0],
                color=colors[level],
                line=dict(color='white', width=2)
            ),
            text=level_nodes,
            textposition='middle center',
            textfont=dict(
                size=[14 if level == 0 else 11 if level == 1 else 9][0],
                color='black'
            ),
            showlegend=False,
            hoverinfo='text',
            hovertext=[f'{name}' for name in level_nodes]
        ))

# Update layout
fig.update_layout(
    title='AgentSchema Hierarchical Structure',
    showlegend=False,
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)

fig.update_xaxes(range=[-5, 7])
fig.update_yaxes(range=[2.5, 5.5])

# Save the chart
fig.write_image('agent_schema_tree.png')