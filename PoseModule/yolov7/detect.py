import torch.backends.cudnn as cudnn
import cv2
import torch
import os

from PoseModule.yolov7.models.experimental import attempt_load
from PoseModule.yolov7.utils.datasets import LoadStreams, LoadImages
from PoseModule.yolov7.utils.plots import colors, plot_one_box
from PoseModule.yolov7.utils.torch_utils import select_device, load_classifier
from PoseModule.yolov7.utils.general import check_img_size, check_imshow, non_max_suppression, apply_classifier, \
    scale_coords, set_logging


class detect:

    def __init__(self, weights, view_img, imgsz, half_precision, kpt_label, device, conf_thres, iou_thres, classes, agnostic_nms, line_thickness) -> None:

        self.imgsz = imgsz
        self.kpts = None
        self.view_img = view_img
        self.kpt_label = kpt_label
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.agnostic_nms = agnostic_nms
        self.line_thickness = line_thickness
        self.classes = classes
        self.weights = weights
        self.half_precision = half_precision
        self.device = device

    def setup(self):
        with torch.no_grad():
            cameras = []
            cam_list = self.check_available_cameras()
            for filename in os.listdir("videos/"):
                if filename.endswith(".mp4"):
                    cam_list.append(f"videos/{filename}")

            set_logging()
            self.device = select_device(self.device)
            self.half = self.device.type != 'cpu' and self.half_precision

            self.model = attempt_load(self.weights, map_location=self.device)
            self.stride = int(self.model.stride.max())

            if isinstance(self.imgsz, (list, tuple)):
                assert len(self.imgsz) == 2
                "height and width of image has to be specified"
                self.imgsz[0] = check_img_size(self.imgsz[0], s=self.stride)
                self.imgsz[1] = check_img_size(self.imgsz[1], s=self.stride)
            else:
                self.imgsz = check_img_size(self.imgsz, s=self.stride)
            self.names = self.model.module.names if hasattr(
                self.model, 'module') else self.model.names

            if self.half:
                self.model.half()

            self.classify = False
            if self.classify:
                self.modelc = load_classifier(name='resnet101', n=2)
                self.modelc.load_state_dict(torch.load(
                    'weights/resnet101.pt', map_location=self.device)['model']).to(self.device).eval()

            if self.device.type != 'cpu':
                self.model(torch.zeros(1, 3, self.imgsz, self.imgsz).to(
                    self.device).type_as(next(self.model.parameters())))

            for source in cam_list:
                source = str(source)
                self.webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
                    ('rtsp://', 'rtmp://', 'http://', 'https://'))
                if self.webcam:
                    cudnn.benchmark = True
                    dataset = LoadStreams(
                        source, img_size=self.imgsz, stride=self.stride)
                else:
                    dataset = LoadImages(
                        source, img_size=self.imgsz, stride=self.stride)
                cameras.append(dataset)
            return cameras

    def detect2(self, dataset):
        with torch.no_grad():
            i = 0
            for path, img, im0s, vid_cap in dataset:
                i += 1
                if i % 20 == 0:
                    img = torch.from_numpy(img).to(self.device)
                    img = img.half() if self.half else img.float()
                    img /= 255.0
                    if img.ndimension() == 3:
                        img = img.unsqueeze(0)
                    pred = []
                    pred = self.model(img, augment=False)[0]
                    pred = non_max_suppression(pred, self.conf_thres, self.iou_thres,
                                               classes=self.classes, agnostic=self.agnostic_nms, kpt_label=self.kpt_label)

                    if self.classify:
                        pred = apply_classifier(pred, self.modelc, img, im0s)

                    mask_list = []
                    helmet_list = []
                    vest_list = []
                    diff_x_list = []
                    diff_y_list = []
                    diff_z_list = []

                    for i, det in enumerate(pred):
                        if isinstance(dataset, LoadStreams):
                            im0 = im0s[i].copy()
                            im1 = im0s[i].copy()
                        elif isinstance(dataset, LoadImages):
                            im0 = im0s.copy()
                            im1 = im0s.copy()

                        if len(det):
                            scale_coords(
                                img.shape[2:], det[:, :4], im0.shape, kpt_label=False)
                            scale_coords(
                                img.shape[2:], det[:, 6:], im0.shape, kpt_label=self.kpt_label, step=3)

                            for det_index, (*xyxy, conf, cls) in enumerate(reversed(det[:, :6])):
                            
                                c = int(cls)
                                label = None if False else (
                                    self.names[c] if False else f'{self.names[c]} {conf:.2f}')
                                kpts = det[det_index, 6:]
                                step = 3
                                nr = 0  # 0-nose, 1-left eye, 2-right eye, 3-left ear, 4-right ear, 5-left shouder, 6-right shouder, 11-left hip, 12-rught hip

                                # mouth point - for mask
                                x_center, y_nose = kpts[step *
                                                        nr], kpts[step * nr + 1]
                                y_shouder_l, y_shouder_r = kpts[step *
                                                                5 + 1], kpts[step * 6 + 1]
                                y_shouders = (
                                    (y_shouder_l + y_shouder_r) / 2)
                                y_center = abs(
                                    (y_shouders - y_nose) / 2.0) + y_nose
                                #cv2.circle(im0, (int(x_center), int(y_center)), 6, (0,0,255), -1)

                                # mask zone
                                x_start_mask = int(kpts[step * 3])
                                x_end_mask = int(kpts[step * 4])
                                y_start_mask = int(y_nose)
                                y_end_height = int(y_center)

                                mask_zone_img = im1[y_start_mask:y_end_height,
                                                        x_end_mask:x_start_mask]

                                

                                mask_list.append(mask_zone_img)
                                cv2.rectangle(im0, (x_start_mask, y_start_mask), (x_end_mask, y_end_height), color=(
                                    0, 255, 255), thickness=2)

                                # helmet zone
                                x_start_helmet = int(kpts[step * 3])
                                x_end_helmet = int(kpts[step * 4])
                                dis = abs(((kpts[step * 1 + 1] + kpts[step * 2 + 1]) / 2) - (
                                    (kpts[step * 5 + 1] + kpts[step * 6 + 1]) / 2))
                                # phi number - gold proportion
                                height_helmet = int(dis * 1.618)
                                y_start_helmet = int(
                                    ((kpts[step * 5 + 1] + kpts[step * 6 + 1]) / 2) - height_helmet * 1.2)
                                y_end_helmet = int(
                                    (kpts[step * 1 + 1] + kpts[step * 2 + 1]) / 2)
                                helmet_zone_img = im1[y_start_helmet:y_end_helmet,
                                                        x_end_helmet:x_start_helmet]
                                helmet_list.append(helmet_zone_img)
                                cv2.rectangle(im0, (x_start_helmet, y_start_helmet), (x_end_helmet, y_end_helmet), color=(
                                    0, 255, 255), thickness=2)

                                # vest zone
                                x_shouder_l, y_shouder_l = int(
                                    kpts[step * 5]), int(kpts[step * 5 + 1])
                                x_hip_r, y_hip_r = int(
                                    kpts[step * 12]), int(kpts[step * 12 + 1])
                                helmet_zone_img = im1[y_shouder_l:y_hip_r,
                                                        x_hip_r:x_shouder_l]
                                vest_list.append(helmet_zone_img)
                                cv2.rectangle(im0, (x_shouder_l, y_shouder_l), (x_hip_r, y_hip_r), color=(
                                    255, 0, 0), thickness=2)

                                # fall detector zone
                                head_x, head_y, head_z = int(
                                    kpts[step * 1]), int(kpts[step * 1 + 1]), kpts[step * 1 + 2]
                                foot_x, foot_y, foot_z = int(
                                    kpts[step * 11]), int(kpts[step * 11 + 1]), kpts[step * 11 + 2]
                                diff_x = abs(head_x-foot_x)
                                diff_y = head_y-foot_y
                                diff_z = abs(head_z-foot_z)
                                diff_x_list.append(diff_x)
                                diff_y_list.append(diff_y)
                                diff_z_list.append(diff_z)
                                # print(f"HEAD:  x: {head_x},    y:{head_y},     z:{head_z}")
                                # print(f"FOOT:  x: {foot_x},    y:{foot_y},     z:{foot_z}")
                                # print(f"diff_x: {diff_x},     diff_y: {diff_y},     diff_z: {diff_z}")

                                # Entire body:
                                #plot_one_box(xyxy, im0, label=label, color=colors(c, True), line_thickness=self.line_thickness, kpt_label=self.kpt_label, kpts=kpts, steps=3, orig_shape=im0.shape[:2])

                        return im0, mask_list, helmet_list, vest_list, im0s, diff_x_list, diff_y_list, diff_z_list

    @staticmethod
    def check_available_cameras():
        cam_list = []
        for i in range(0, 10):
            cap = cv2.VideoCapture(i)
            if cap is None or not cap.isOpened():
                pass
            else:
                cam_list.append(i)
        return cam_list
