import cv2
import numpy

class JsonObject():
  def __init__(self, type, uuid, x, y, width, height, element, name, parents):
    self.type = type
    self.uuid = uuid
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.element = element
    self.name = name
    self.parents = parents

  def to_json():
    json_str = ''
    json_str += '{'
    json_str += '"type": ' + type + ','
    json_str += '"uuid": ' + uuid + ','
    json_str += '"x": ' + x + ','
    json_str += '"y": ' + y + ','
    json_str += '"width": ' + width + ','
    json_str += '"height": ' + height + ','
    json_str += '"element": ' + element + ','
    json_str += '"name": ' + name + ','
    json_str += '"parents": ' + parents + ','
    json_str += '}'

def mock():
  img_path = 'example-network-topology-2.png'

  objects = [[ 48.6001,  97.3796,  96.5179, 143.4916],
        [ 45.8036, 339.0088,  90.1675, 399.4269],
        [ 10.9968, 427.6397, 191.3152, 467.7309],
        [754.6960, 110.9679, 803.4858, 161.2734],
        [475.6418,  91.7320, 545.5679, 141.8133],
        [282.3315,  38.0931, 339.3317, 128.1587],
        [327.5374, 107.3355, 390.5792, 164.9739],
        [567.1105, 114.8102, 633.4964, 162.0698]]

  determine_network_topology(img_path, objects)

def determine_network_topology(img_path, objects):
  lines = get_lines(img_path)
  lines = reject_vertical_lines(lines)
  minimum_x, maximum_x, minimum_y, maximum_y, maximum_sum_x, maximum_sum_y, most_common_x, most_common_y = determine_main_network_lines(img_path, lines)
  render_lines(img_path, lines)

  start_x, start_y = find_start(img_path, object, most_common_y)
  traverse(img_path, objects, start_x, start_y)

def traverse(img_path, objects, start_x, start_y):
  curr_x = start_x
  curr_y = start_y
  nodes = []
  edges = []
  img = cv2.imread(cv2.samples.findFile(img_path))
  height, width, _ = img.shape
  latest_node_id = -1

  for o in objects:
    x1, y1, x2, y2 = round(o[0]), round(o[1]), round(o[2]), round(o[3])
    cv2.rectangle(img, (x1, y1), (x2, y2), color=(255,0,0), thickness=2)

  while True:
    print(curr_x)

    """cv2.circle(img, (round(curr_x), round(curr_y)), 2, (0, 255, 0), 2)
    render(img)"""

    # Check if intersecting with bounding box of an object
    collided, collided_index = check_collision(objects, curr_x, curr_y)

    if collided:
      nodes.append(collided_index)
      cv2.circle(img, (round(curr_x), round(curr_y)), 5, (0, 0, 255), 5)

      if (latest_node_id != -1):
        edges.append((latest_node_id, collided_index))

      latest_node_id = collided_index

      curr_x += objects[collided_index][2] - objects[collided_index][0]
    else:
      curr_x += 1

    # Bounds check
    if curr_x >= width - 1 or curr_y >= height:
      print("Reached limit")
      break

  print(nodes)
  print(edges)

def render(img):
  cv2.imshow("Render", img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

def check_collision(objects, curr_x, curr_y):
  """
  Could theoretically improved so that an iteration over all objects is not required,
  but hey, time constraints ;-)
  """
  i = 0
  for obj in objects:
    x1, y1, x2, y2 = obj[0], obj[1], obj[2], obj[3]
    if curr_x >= x1 and curr_x <= x2 and curr_y >= y1 and curr_y <= y2:
      print("COLLISION")
      print(i)
      print(obj)
      return True, i
    i += 1
  return False, -1

def find_start(img_path, lines, most_common_y):
  img = cv2.imread(cv2.samples.findFile(img_path))
  _, width, _ = img.shape
  start_x = 0
  for i in range(0, width):
    if img[most_common_y][i][0] <= 25 :
      print("HEHE")
      print(i)
      print(most_common_y)
      start_x = i
      break
  cv2.circle(img, (start_x, most_common_y), 5, (255, 0, 0), 5)
  render(img)
  return start_x, most_common_y

def get_lines(img_path):
  img = cv2.imread(cv2.samples.findFile(img_path))
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  edges = cv2.Canny(gray, 50, 100, apertureSize = 3)
  lines = cv2.HoughLinesP(edges, 1, numpy.pi/180, 100, minLineLength=70, maxLineGap=10)
  print("ok")
  return lines

def reject_vertical_lines(lines):
  new_lines = []
  for line in lines:
    if line[0][0] != line[0][2]:
      new_lines.append(line)

  return new_lines

def render_lines(img_path, lines):
  img = cv2.imread(cv2.samples.findFile(img_path))
  for line in lines:
    x1, y1, x2, y2 = line[0]
    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
  render(img)

def determine_main_network_lines(img_path, lines):
  """
  Ideas: 
    - get longest lines
    - get maximum extent
    - sum of coordinates
  """
  minimum_x = 999999
  maximum_x = -999999
  minimum_y = 999999
  maximum_y = -999999

  sum_x_to_y_map = dict()
  sum_y_to_x_map = dict()

  for line in lines:
    x1, y1, x2, y2 = line[0][0], line[0][1], line[0][2], line[0][3]

    thresh = 5
    if y1 >= y2 + thresh or y1 <= y2 - thresh:
      continue

    minimum_x = min(minimum_x, x1, x2)
    minimum_y = min(minimum_y, y1, y2)
    maximum_x = max(maximum_x, x1, x2)
    maximum_y = max(maximum_y, y1, y2)

    sum_x_to_y_map[x1] = sum_x_to_y_map.get(x1, 0) + (y2 - y1)
    sum_y_to_x_map[y1] = sum_y_to_x_map.get(y1, 0) + (x2 - x1)

  maximum_sum_x = 0
  maximum_sum_y = 0
  most_common_x = 0
  most_common_y = 0

  for k, v in sum_x_to_y_map.items():
    if v > maximum_sum_y:
      maximum_sum_y = v
      most_common_x = k

  for k, v in sum_y_to_x_map.items():
    if v > maximum_sum_x:
      maximum_sum_x = v
      most_common_y = k

  print(minimum_x)
  print(maximum_x)
  print(minimum_y)
  print(maximum_y)

  print(maximum_sum_x)
  print(maximum_sum_y)
  print(most_common_x)
  print(most_common_y)

  return (minimum_x, maximum_x, minimum_y, maximum_y, maximum_sum_x, maximum_sum_y, most_common_x, most_common_y)

mock()