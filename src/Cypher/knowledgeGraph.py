from pathlib import Path
from py2neo import Graph, NodeMatcher, RelationshipMatcher
class knowledgeGraph:
    def __init__(self, clear=False):
        self.nodes = {}  # 节点: label
        self.g = self.connect_neo4j()
        self.nodes_matcher = NodeMatcher(self.g)
        self.relationship_matcher = RelationshipMatcher(self.g)
        self.delete_query = "MATCH (n) DETACH DELETE n"  # 清空图谱指令 如果clear为True 则清空图谱
        self.relation_set = set()
        self.entity_set = set()
        self.samples = []
        if clear:
            self.clear_before_build()

    @staticmethod
    def connect_neo4j(username="neo4j", password="613613zzk"):
        my_graph = Graph("neo4j@bolt://localhost:7687", auth=(username, password))
        return my_graph

    def clear_before_build(self):
        try:
            self.g.run(self.delete_query).evaluate()
            print("cleared all")
        except Exception as e:
            print(str(e))

    def run_cypher(self, cypher_batch):
        cypher = '\n'.join(cypher_batch)
        cyphers = cypher.strip().split(";")
        for c in cyphers:
            if c == "":
                continue
            try:
                self.g.run(c).evaluate()
                # print(f"Cypher {c} done. Got ret {ret}")
            except Exception as e:
                print(c, str(e))
                break
def process_cypher(kg, path):
    txt_root = Path(path)
    for txt in txt_root.rglob("*.txt"):
        print(f"extracting file {str(txt)}")
        with open(str(txt), 'r', encoding='utf-8') as f:
            contents = f.readlines()
        kg.run_cypher(contents)

    
if __name__ == '__main__':    
    # 存入图谱
    # MATCH (n) DETACH DELETE n
    knowledge_graph = knowledgeGraph(clear = False)

    # process_cypher(knowledge_graph, "result/node")
    process_cypher(knowledge_graph, "result/relation")

# python src/Cypher/KnowledgeGraph.py