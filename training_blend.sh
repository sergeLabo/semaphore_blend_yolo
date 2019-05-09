./darknet detector train blend/obj.data blend/yolov3-obj_3l_blend.cfg darknet53.conv.74 -map

# reprise
./darknet detector train blend/obj.data blend/yolov3-obj_3l_blend.cfg blend/backup/yolov3-obj_3l_blend_5000.weights -map
