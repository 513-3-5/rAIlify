require "json"

file = File.read('example.json')
data = JSON.parse(file)

nodes = data.filter { |node| node["type"] == "node" }.sort_by { |node| [node["originX"], node["originY"]] }
edges = data.filter { |node| node["type"] == "edge" }

visualizing_array = [[nodes[0]]]
nodes.shift

loop do
  next_level = []
  visualizing_array.last.each do |node|
    next_level += edges.find_all { |edge| edge["parents"].include?(node["uuid"]) }
    edges.each { |edge| edge["parents"].delete_if { |parent| parent == node["uuid"] } }
  end
  visualizing_array << next_level.uniq
  new_level = []
  visualizing_array.last.each do |edge|
    new_level += edge["parents"].map { |parent| nodes.find { |node| node["uuid"] == parent } }
    nodes.delete_if { |node| edge["parents"].find { |parent| node["uuid"] == parent } }
    edges.each { |original_edge| edge["parents"] = [] if original_edge["uuid"] == edge["uuid"]}
  end
  visualizing_array << new_level.uniq
  break if nodes.empty?
end

width = visualizing_array.map(&:length).max

visualizing_array.map do |row|
  (width - (row.length / 2)).times { print " " }
  row.map do |column|
    print "|" if column["element"] == "Gleisabschnitt"
    print "*" if column["element"] == "Radzähler"
    print "^" if column["element"] == "Weiche"
    print " "
  end
  print "\n"
end
