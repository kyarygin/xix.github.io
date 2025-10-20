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
        {
            **{'id': index},
            **process_full_name(row['full_name']),
            **row,
            **{'tags': [x for x in row['tags'].split(',') if x != 'nan']}
        }
        for index, row in pd.read_csv(nodes_file, sep = ';').astype(str).iterrows()
    ]
    groups = {node['group'] for node in nodes}
    group2id = {group: group_id for group_id, group in enumerate(list(groups))}
    for node in nodes:
        node['group_id'] = group2id[node['group']]
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

def format_pair(key: str, value: str) -> str:
    if isinstance(value, int):
        return f'{key}: {value}'
    if isinstance(value, list):
        value_str = ', '.join(f'"{x}"' for x in value)
        return f'{key}: [{value_str}]'
    return f'{key}: \"{value}\"'

def build_js_string(nodes, edges):
    nodes_str = ",\n".join(
        ' '*16 + '{' + ', '.join(format_pair(key, value) for key, value in node.items()) + '}'
        for node in nodes
    )
    links_str = ",\n".join(
        ' '*16 + '{' + ', '.join(format_pair(key, value) for key, value in edge.items()) + '}'
        for edge in edges
    )
    return (
        '\n' + ' ' * 12 +
        f"nodes: [\n{nodes_str}\n" +
        ' ' * 12 + '],' +
        '\n' + ' ' * 12 +
        f"links: [\n{links_str}\n" +
        ' ' * 12 + ']'
    )

if __name__ == '__main__':
    nodes, edges = load_data('nodes.csv', 'edges.csv')
    output_str = build_js_string(nodes, edges)

    with open('index.html', 'r') as f:
        input_file = f.read()
    output_file = re.sub(r'(const graph = {)(.*?)(\s+};)', fr"\1{output_str}\3", input_file, flags=re.DOTALL)
    with open('index.html', 'w') as f:
        f.write(output_file)
