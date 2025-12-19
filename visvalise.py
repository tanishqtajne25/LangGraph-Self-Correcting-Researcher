from graph import build_graph

# 1. Build the graph
app = build_graph()

# 2. Generate the Mermaid diagram as PNG bytes
print("Generating graph visualization...")

png_bytes = app.get_graph().draw_mermaid_png()

    # 3. Save to a file
output_file = "agent_workflow.png"
with open(output_file, "wb") as f:
    f.write(png_bytes)
    
print(f" Graph saved as '{output_file}'")

