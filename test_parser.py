from my_parser import parse

code = '''
int main() {
    int a = 5;
    float b = 2.5;
    if (a > b) {
        return a;
    }
    return 0;
}
'''

tree = parse(code)

if tree:
    dot = tree.to_graphviz()
    dot.render('parse_tree', format='png', view=True)
else:
    print("❌ Parse tree generation failed.")
