require "json"

ARGV.each do |filename|
  file = File.read(filename)
  data = JSON.parse(file)


  tracks = data.filter { |data_obj| data_obj['element'] == 'Tracknumber' }.sort_by { |node| [node['originX'], node['originY']] }
  edges = data.filter { |data_obj| data_obj['type'] == 'edge' }

  tracks.each do |track|
    track_edges = edges.find_all { |edge| edge['parents'].include?(track['uuid']) }
    track_edges.first['parents'].find { |parent| parent == track['uuid'] }
    new_track_edge = {
      "type"=>"edge",
      "uuid"=>track['uuid'],
      "originX"=>nil,
      "originY"=>nil,
      "width"=>nil,
      "height"=>nil,
      "element"=>"Tracknumber",
      "name"=>track['name'],
      "parents"=>track_edges.map { |track_edge| track_edge['parents'].find { |perent| perent != track['uuid'] } }
    }
    pp new_track_edge
    data << new_track_edge
    data.delete(track)
    track_edges.each { |edge| data.delete(edge) }
  end

  File.open("input/corrected_#{filename.split('/').last.split('.').first}.json", 'w') do |file|
    file.write(data.to_json)
  end
end