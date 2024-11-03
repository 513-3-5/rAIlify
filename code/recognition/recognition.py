import cv2
import numpy
import torch
import ultralytics

CLASS_MAINSIGNAL = 0
CLASS_RADZAEHLER = 1
CLASS_TRACKJOINT = 2
CLASS_TRACKNUMBER = 3
CLASS_WEICHE = 4

def cls_to_str(cls_id):
  class_map = ['Mainsignal', 'Radzähler', 'Trackjoint', 'Tracknumber', 'Weiche']
  return class_map[cls_id]

class GraphEntity():
  """
  This is pretty ugly and optimally, you'd do this in another way,
  but hey, time constraints 
  """
  def __init__(self, o_type, uuid, x, y, width, height, element, name, parents):
    self.o_type = str(o_type)
    self.uuid = str(uuid)
    self.x = str(x)
    self.y = str(y)
    self.width = str(width)
    self.height = str(height)
    self.element = str(element)
    self.name = str(name)
    self.parents = ','.join(f'"{str(i)}"' for i in parents)

  def to_json_str(self):
    json_str = ''
    json_str += '{'
    json_str += '"type": "' + self.o_type + '",'
    json_str += '"uuid": "' + self.uuid + '",'
    json_str += '"originX": ' + self.x + ','
    json_str += '"originY": ' + self.y + ','
    json_str += '"width": ' + self.width + ','
    json_str += '"height": ' + self.height + ','
    json_str += '"element": "' + self.element + '",'
    json_str += '"name": "' + self.name + '",'
    json_str += '"parents": ['+ self.parents + ']'
    json_str += '}'
    return json_str

class Classify:
  def __init__(self):
    pass

  def classify(self, img_path):
    model = ultralytics.YOLO('yolo/yolo11ltrained.pt')
    results = model(img_path)
    crh = ClassificationResultHandler()
    results = crh.generate_classified_objects(results)
    nr = NetworkRecognizer(img_path, results)
    json = nr.determine_network_topology()
    return json

class ClassifiedObject:
  def __init__(self, o_id, cls_id, bb_coords, confidence):
    self.o_id = o_id
    self.bb_coords = bb_coords
    self.cls_id = cls_id
    self.confidence = confidence

class ClassificationResultHandler:
  def __init__(self):
    pass

  # TODO(amartabakovic)
  def generate_classified_objects(self, classification_results):
    objs = []
    for result in classification_results:
      count = len(result.boxes.cls)
      for i in range(0, count):
        cls_id = result.boxes.cls[i].int()
        conf = result.boxes.conf[i]
        bb_coords = (result.boxes.xyxy[i][0].item(), result.boxes.xyxy[i][1].item(), result.boxes.xyxy[i][2].item(), result.boxes.xyxy[i][3].item())
        new_obj = ClassifiedObject(i, cls_id, bb_coords, conf)
        objs.append(new_obj)
    return objs

class NetworkRecognizer:
    """
    A few ideas and observations:
    - There is in most network plans a y-coordinate which has the highest
      occurrence of lines. This line is used as the central line 
      for traversing and building the network.
    - The symbol classification returns us bounding boxes and coordinates,
      which can be used for traversal.
    - We always move from left to right.
    - We never move completely vertically
    """
    def __init__(self, img_path, objects):
        self._img_path = img_path
        self._img = cv2.imread(cv2.samples.findFile(self._img_path))
        self._debug_img = self._img.copy()
        self._objects = objects  # List of ClassifiedObject instances

    def determine_network_topology(self):
        main_lines = self._get_lines(self._img)
        horizontal_lines = self._filter_horizontal_lines(main_lines)
        boundaries, common_points = self._determine_main_network_lines(horizontal_lines)
        
        self._draw_lines(horizontal_lines)

        start_x, start_y = self._find_start(boundaries, common_points['most_common_y'])
        json = self._traverse_network(start_x, start_y)

        # self._render()
        return json

    def _traverse_network(self, start_x, start_y):
        json_result = []
        curr_x, curr_y = start_x, start_y
        nodes, edges = [], []
        latest_node_id = -1
        height, width, _ = self._img.shape

        available_edge_id = 0

        self._draw_object_bbs()

        while curr_x < width and curr_y < height:
            collided, node_id = self._check_collision(curr_x, curr_y)

            if collided:
                nodes.append(node_id)

                # new json entry for node
                node = self._objects[node_id]
                center_x = node.bb_coords[0] + (node.bb_coords[2] - node.bb_coords[0]) / 2
                center_y = node.bb_coords[1] + (node.bb_coords[3] - node.bb_coords[1]) / 2
                w = node.bb_coords[2] - node.bb_coords[0]
                h = node.bb_coords[3] - node.bb_coords[1]
                new_json_entry = GraphEntity('node', node_id, center_x,  center_y, w, h, cls_to_str(node.cls_id), '', '')
                json_result.append(new_json_entry)

                self._draw_node(curr_x, curr_y)

                if latest_node_id != -1:
                    edges.append((latest_node_id, node_id))

                    # new json entry for edge
                    new_json_entry = GraphEntity('edge', available_edge_id, 'null', 'null', 'null', 'null', 'gleisabschnitt', '', [latest_node_id, node_id])
                    json_result.append(new_json_entry)
                    available_edge_id += 1

                # TODO(amartabakovic): Check if weiche
                if self._objects[node_id].cls_id == CLASS_WEICHE:
                  #handle_weiche()
                  pass

                # Move to end of the current object based on its bounding box
                latest_node_id = node_id
                curr_x += self._objects[node_id].bb_coords[2] - self._objects[node_id].bb_coords[0]
            else:
                curr_x += 1  # Increment x if no collision

        return '[' + ','.join(j.to_json_str() for j in json_result) + ']'

    def _draw_node(self, x, y):
        cv2.circle(self._debug_img, (round(x), round(y)), 5, (0, 0, 255), 5)

    def _draw_object_bbs(self):
        for obj in self._objects:
            x1, y1, x2, y2 = map(round, obj.bb_coords)
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
        for i, obj in enumerate(self._objects):
            x1, y1, x2, y2 = obj.bb_coords
            if x1 <= x <= x2 and y1 <= y <= y2:
                return True, i
        return False, -1

    def _find_start(self, boundaries, most_common_y):
        _, width, _ = self._img.shape

        for x in range(width):
            if self._img[most_common_y, x, 0] <= 70:  # Dark line found
                self._draw_node(x, most_common_y)
                # self._render(title="Starting Point")
                return x, most_common_y
        return 0, most_common_y

    def _get_lines(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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