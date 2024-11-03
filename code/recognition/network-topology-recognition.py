import cv2
import numpy

class GraphEntity():
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

  def to_json_str():
    json_str = ''
    json_str += '{'
    json_str += '"type": ' + type + ','
    json_str += '"uuid": ' + uuid + ','
    json_str += '"origin_x": ' + x + ','
    json_str += '"origin_y": ' + y + ','
    json_str += '"width": ' + width + ','
    json_str += '"height": ' + height + ','
    json_str += '"element": ' + element + ','
    json_str += '"name": ' + name + ','
    json_str += '"parents": ' + parents + ','
    json_str += '}'

# TODO(amartabakovic): Inteface with the rest of the system
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
  """
  result = objects
  res_handler = ClassificationResultHandler()
  classified_objs = res_handler.generate_classified_objects(result)
  """
  nr = NetworkRecognizer(img_path, objects)
  nr.determine_network_topology()

class ClassifiedObject():
  def __self__(self, bb_coords, cls_id, cls_name, confidence):
    self.bb_coords = bb_coords
    self.cls_id = cls_id
    self.cls_name = cls_name
    self.confidence = confidence

class ClassificationResultHandler():
  def __self__(self):
    pass

  # TODO(amartabakovic)
  def generate_classified_objects(self, classification_results):
    for result in results:
      count = len(classification_result.boxes.cls)
      for i in range(0, count):
        pass

class NetworkRecognizer():
  def __init__(self, img_path, objects):
    self._img_path = img_path
    self._img = cv2.imread(cv2.samples.findFile(self._img_path))
    self._debug_img = self._img.copy()
    self._objects = objects

  def determine_network_topology(self):
    lines = self._get_lines()
    horizontal_lines = self._filter_horizontal_lines(lines)
    boundaries, common_points = self._determine_main_network_lines(horizontal_lines)
    
    self._draw_lines(horizontal_lines)

    start_x, start_y = self._find_start(boundaries, common_points['most_common_y'])
    self._traverse_network(start_x, start_y)

    self._render()

  def _traverse_network(self, start_x, start_y):
    curr_x, curr_y = start_x, start_y
    nodes, edges = [], []
    latest_node_id = -1
    height, width, _ = self._img.shape

    self._draw_object_bbs()

    while curr_x < width and curr_y < height:
      collided, node_id = self._check_collision(curr_x, curr_y)

      if collided:
        nodes.append(node_id)
        self._draw_node(curr_x, curr_y)

        if latest_node_id != -1:
          edges.append((latest_node_id, node_id))

        latest_node_id = node_id
        curr_x += self._objects[node_id][2] - self._objects[node_id][0]  # Move to end of current object
      else:
        curr_x += 1  # Increment x if no collision

    print("Nodes:", nodes)
    print("Edges:", edges)

  def _draw_node(self, x, y):
    cv2.circle(self._debug_img, (round(x), round(y)), 5, (0, 0, 255), 5)

  def _draw_object_bbs(self):
    for obj in self._objects:
      x1, y1, x2, y2 = map(round, obj)
      cv2.rectangle(self._debug_img, (x1, y1), (x2, y2), color=(255, 0, 0), thickness=2)

  def _draw_lines(self, lines):
    for line in lines:
      x1, y1, x2, y2 = line[0]
      cv2.line(self._debug_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
  

  def _render(self, title="Render"):
    cv2.imshow(title, self._debug_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

  def _check_collision(self, x, y):
    for i, (x1, y1, x2, y2) in enumerate(self._objects):
      if x1 <= x <= x2 and y1 <= y <= y2:
        return True, i
    return False, -1

  def _find_start(self, boundaries, most_common_y):
    _, width, _ = self._img.shape

    for x in range(width):
      if self._img[most_common_y, x, 0] <= 70:  # Dark line found
        self._draw_node(x, most_common_y)
        self._render(title="Starting Point")
        return x, most_common_y
    return 0, most_common_y

  def _get_lines(self):
    gray = cv2.cvtColor(self._img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 100, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, numpy.pi / 180, threshold=100, minLineLength=70, maxLineGap=10)
    return lines

  def _filter_horizontal_lines(self, lines, angle_threshold=5):
    horizontal_lines = [line for line in lines if abs(line[0][1] - line[0][3]) <= angle_threshold]
    return horizontal_lines

  def _determine_main_network_lines(self, lines):
    boundaries = {
      'min_x': float('inf'), 'max_x': float('-inf'),
      'min_y': float('inf'), 'max_y': float('-inf')
    }
    x_to_y_sum = {}
    y_to_x_sum = {}

    for line in lines:
      x1, y1, x2, y2 = line[0]

      boundaries['min_x'] = min(boundaries['min_x'], x1, x2)
      boundaries['min_y'] = min(boundaries['min_y'], y1, y2)
      boundaries['max_x'] = max(boundaries['max_x'], x1, x2)
      boundaries['max_y'] = max(boundaries['max_y'], y1, y2)

      x_to_y_sum[x1] = x_to_y_sum.get(x1, 0) + (y2 - y1)
      y_to_x_sum[y1] = y_to_x_sum.get(y1, 0) + (x2 - x1)

    most_common_x = max(x_to_y_sum, key=x_to_y_sum.get, default=0)
    most_common_y = max(y_to_x_sum, key=y_to_x_sum.get, default=0)

    return boundaries, {'most_common_x': most_common_x, 'most_common_y': most_common_y}

mock()