from py2neo import Graph
graph = Graph("bolt://localhost:7687", auth=("neo4j", "613613zzk"))
# 删除所有自引用的关系边
delete_self_relations_query = """
    MATCH (n:operator)-[r:equivalentOperator]->(m)
    WHERE id(n) = id(m)
    DELETE r
"""
# 删除所有重复的parameterOfOperator边
delete_duplicate_relations_query = """
    MATCH (n)-[r1:parameterOfOperator]->(m), (n)-[r2:parameterOfOperator]->(m)
    WHERE id(r1) < id(r2)
    DELETE r2
"""
# 删除所有重复的equivalOperator边
delete_duplicate_equival_relations_query = """
    MATCH (n)-[r1:equivalentOperator]->(m), (n)-[r2:equivalentOperator]->(m)
    WHERE id(r1) < id(r2)
    DELETE r2
"""
# 删除所有重复的equivalParameter边
delete_duplicate_equival_relations_query = """
    MATCH (n)-[r1:equivalentParameter]->(m), (n)-[r2:equivalentParameter]->(m)
    WHERE id(r1) < id(r2)
    DELETE r2
"""
graph.run(delete_self_relations_query)
graph.run(delete_duplicate_relations_query)
graph.run(delete_duplicate_equival_relations_query)

# python src/PaddlePaddle2Mindspore/help.py