require "json"
require "rgl/adjacency"
require 'rgl/dot'

ARGV.each do |filename|
  file = File.read(filename)
  data = JSON.parse(file)


  nodes = data.filter { |data_obj| data_obj['type'] == 'node' }.sort_by { |node| [node['originX'], node['originY']] }
  objects = data.filter { |data_obj| data_obj['type'] == 'object' }.sort_by { |object| [object['originX'], object['originY']] }
  edges = data.filter { |data_obj| data_obj['type'] == 'edge' }

  graph = RGL::AdjacencyGraph.new

  nodes.each do |node|
    graph.add_vertex(node['uuid'])
    graph.set_vertex_options(node['uuid'], label: "#{node['element']}\n#{node['name']}", group: 'track', shape: 'box')
  end

  edges.each do |edge|
    graph.add_edge(edge['parents'][0], edge['parents'][1])
    graph.set_edge_options(edge['parents'][0], edge['parents'][1], label: "#{edge['name']}")
  end

  objects.each do |object|
    unless object['parents'].empty?
      graph.add_edge(object['uuid'], object['parents'][0])
      graph.set_vertex_options(object['uuid'], label: "#{object['element']}\n#{object['name']}", shape: 'plain')
      graph.set_edge_options(object['uuid'], object['parents'][0], style: 'dotted' )
    end
  end

  graph.write_to_graphic_file('png', "output/#{filename.split(".").first}")
end
