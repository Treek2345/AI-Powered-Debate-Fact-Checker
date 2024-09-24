import plotly.graph_objs as go
import plotly.express as px
import networkx as nx

def create_timeline(fact_checks):
    data = []
    for i, (claim, result, speaker) in enumerate(fact_checks):
        data.append(dict(
            Claim=claim,
            Start=i,
            Finish=i+1,
            Speaker=speaker,
            Verification=result.get("Verification", "N/A")
        ))
    
    fig = px.timeline(data, x_start="Start", x_end="Finish", y="Speaker", color="Verification",
                      hover_data=["Claim"])
    fig.update_layout(title="Timeline of Claims")
    return fig

def create_network_graph(fact_checks):
    G = nx.Graph()
    
    for claim, result, speaker in fact_checks:
        G.add_node(speaker, node_type='speaker')
        categories = result.get("Categories", [])
        for category in categories:
            G.add_node(category, node_type='category')
            G.add_edge(speaker, category)
    
    pos = nx.spring_layout(G)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    node_adjacencies = []
    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_adjacencies.append(len(adjacencies[1]))
        node_text.append(f'{adjacencies[0]} # of connections: {len(adjacencies[1])}')

    node_trace.marker.color = node_adjacencies
    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    title='Network Graph of Speakers and Topics',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )
    return fig

def generate_summary(fact_checks):
    # This is a simple summary generation. For a more sophisticated summary,
    # you might want to use the Groq API or another language model.
    verified_claims = [claim for claim, result, _ in fact_checks if result.get("Verification") == "VERIFIED"]
    unverified_claims = [claim for claim, result, _ in fact_checks if result.get("Verification") == "NOT VERIFIED"]
    
    summary = f"""
    Debate Summary:
    
    Total claims analyzed: {len(fact_checks)}
    Verified claims: {len(verified_claims)}
    Unverified claims: {len(unverified_claims)}
    
    Key verified points:
    {', '.join(verified_claims[:3])}
    
    Key points needing further verification:
    {', '.join(unverified_claims[:3])}
    """
    
    return summary