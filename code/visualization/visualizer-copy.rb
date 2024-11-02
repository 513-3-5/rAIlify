require "json"
require "rgl/adjacency"
file = File.read('example.json')
data = JSON.parse(file)


nodes = data.filter { |node| node["type"] == "node" }.sort_by { |node| [node["originX"], node["originY"]] }
edges = data.filter { |node| node["type"] == "edge" }

graph = RGL::AdjacencyGraph.new

nodes.each { |node| graph.add_vertex(node) }
edges.each { |edge| 
  u = graph.find { |vertex| vertex['uuid'] == edge['parents'][0] } 
  v = graph.find { |vertex| vertex['uuid'] == edge['parents'][1] } 

  graph.add_edge(u,v)
}


graph.each {|item| pp item}