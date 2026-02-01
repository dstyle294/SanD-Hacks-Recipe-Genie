from ObjDet import getItems
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
example_image_path = os.path.join(script_dir, 'images', 'pantry.jpg')

groceries_list = getItems(image_path=example_image_path)

print(groceries_list)
