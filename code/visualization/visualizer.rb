require "json"
require "rgl/adjacency"
require 'rgl/dot'

ARGV.each do |filename|
  file = File.read(filename)
  data = JSON.parse(file)


  nodes = data.filter { |data_obj| data_obj["type"] == "node" }.sort_by { |node| [node["originX"], node["originY"]] }
  objects = data.filter { |data_obj| data_obj["type"] == "object" }.sort_by { |object| [object["originX"], object["originY"]] }
  edges = data.filter { |data_obj| data_obj["type"] == "edge" }

  graph = RGL::AdjacencyGraph.new
  nodes.each { |node| graph.add_vertex(node) }

  edges.each do |edge|
    u = graph.find { |vertex| vertex['uuid'] == edge['parents'][0] }
    v = graph.find { |vertex| vertex['uuid'] == edge['parents'][1] }
    graph.add_edge(u, v)
    graph.set_edge_options(u, v, label: "#{edge['name']}")
  end

  objects.each do |object|
    unless object['parents'].empty?
      v = graph.each_vertex.find { |vertex| vertex['uuid'] == object['parents'][0] }
      graph.add_edge(object, v)
      graph.set_edge_options(object, v, style: 'dotted' )
    end
  end

  graph.each_vertex { |vertex| graph.set_vertex_options(vertex, label: "#{vertex['element']}\n#{vertex['name']}") }
  graph.write_to_graphic_file('png', "output/#{filename.split(".").first}")
end
