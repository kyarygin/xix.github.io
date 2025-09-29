import pandas as pd
import re

def process_full_name(full_name: str):
    name, patronymic, surname = full_name.split(' ', 2)
    return {
        # 'full_name': full_name,
        'short_name': f'{name} {surname}',
        'abr_name': f'{name[0]}.{patronymic[0]}. {surname}'
    }

def load_data(nodes_file: str, edges_file: str):
    nodes = [
        dict(
            **{'id': index},
            **process_full_name(row['full_name']),
            **row
        )
        for index, row in pd.read_csv(nodes_file, sep = ';').iterrows()
    ]
    full_name2id = {node['full_name']: node['id'] for node in nodes}
    edges = [
        dict(
            **{
                "source": full_name2id[row['full_name_1']],
                "target": full_name2id[row['full_name_2']]
            },
            **row
        )
        for index, row in pd.read_csv(edges_file, sep = ';').iterrows()
    ]
    return nodes, edges

def build_js_string(nodes, edges):
    nodes_str = ",\n".join(
        '{' + ', '.join(f'{key}: \"{value}\"' for key, value in node.items()) + '}'
        for node in nodes
    )
    links_str = ",\n".join(
        '{' + ', '.join(f'{key}: \"{value}\"' for key, value in edge.items()) + '}'
        for edge in edges
    )
    return f"\nnodes: [\n{nodes_str}\n],\nlinks: [\n{links_str}\n]"

if __name__ == '__main__':
    nodes, edges = load_data('nodes.csv', 'edges.csv')
    output_str = build_js_string(nodes, edges)

    with open('index.html', 'r') as f:
        input_file = f.read()
    output_file = re.sub(r'(const graph = {)(.*?)(};)', fr"\1{output_str}\3", input_file, flags=re.DOTALL)
    with open('index.html', 'w') as f:
        f.write(output_file)
