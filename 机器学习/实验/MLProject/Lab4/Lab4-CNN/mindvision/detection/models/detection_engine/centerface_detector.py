# Copyright 2020-21 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""centerface detector"""

import json
import os
import pickle

import numpy as np
from datasets.pipelines.transforms import get_affine_transform, affine_transform
from models.detection_engine.external.bbox import bbox_overlaps
from models.detection_engine.external.nms import soft_nms
from scipy.io import loadmat

from mindvision.engine.class_factory import ClassFactory, ModuleType


@ClassFactory.register(ModuleType.DETECTION_ENGINE)
class CenterfaceDetectionEngine:
    """ Centerface DetectionEngine. """

    def __init__(self, num_classes, nms, test_scales, k_num, iou_thresh, reg_offset, \
                 save_path, ground_truth_path, eval_imageid_file):
        self.test_scales = test_scales
        self.num_classes = num_classes
        self.nms = nms
        self.reg_offset = reg_offset
        self.k_num = k_num
        self.iou_thresh = iou_thresh  # 0.4
        self.gt_path = ground_truth_path
        self.eval_imageid_file = eval_imageid_file
        self.save_path = save_path

    def post_process(self, dets, meta, scale=1):
        """
        Post process process
        """
        dets = dets.reshape(1, -1, dets.shape[2])
        dets = multi_pose_post_process(
            dets.copy(), [meta['c']], [meta['s']],
            meta['out_height'], meta['out_width'])
        for j in range(1, self.num_classes + 1):
            dets[0][j] = np.array(dets[0][j], dtype=np.float32).reshape(-1, 15)
            dets[0][j][:, :4] /= scale
            dets[0][j][:, 5:] /= scale
        return dets[0]

    def merge_outputs(self, detections):
        """
        Merge detection outputs
        """
        results = {}
        results[1] = np.concatenate([detection[1] for detection in detections], axis=0).astype(np.float32)
        if self.nms or len(self.test_scales) > 1:
            soft_nms(results[1], Nt=0.5, method=2)
        results[1] = results[1].tolist()
        return results

    def detect(self, args, **kwargs):
        """
        detection outputs
        """
        output_hm = args[0].asnumpy().astype(np.float32)
        output_wh = args[1].asnumpy().astype(np.float32)
        output_off = args[2].asnumpy().astype(np.float32)
        output_kps = args[3].asnumpy().astype(np.float32)
        topk_inds = args[4].asnumpy().astype(np.long)
        image_id = kwargs['image_id']
        meta = {}
        c = kwargs['c'][0].asnumpy()
        s = kwargs['s'].asnumpy()[0]
        out_height = kwargs['out_height'].asnumpy()[0]
        out_width = kwargs['out_width'].asnumpy()[0]
        meta = {'c': c, 's': s, 'out_height': out_height, 'out_width': out_width}

        reg = output_off if self.reg_offset else None

        detections = []
        for scale in self.test_scales:
            dets = self.centerface_decode(output_hm, output_wh, output_kps, \
                                          reg=reg, opt_k=self.k_num, topk_inds=topk_inds)

            dets = self.post_process(dets, meta, scale)  # box:4+score:1+kpoints:10+class:1=16     ## --3: post_process

            detections.append(dets)

        results = self.merge_outputs(detections)  # --4: merge_outputs
        with open(self.eval_imageid_file, 'r') as load_f:
            load_dict = json.load(load_f)

        img_dir = load_dict[image_id - 1]['im_dir']
        img_name = load_dict[image_id - 1]['im_name']

        save_path = self.save_path
        if not os.path.exists(save_path + img_dir):
            os.makedirs(save_path + img_dir)

        f = open(save_path + img_dir + '/' + img_name + '.txt', 'w')
        f.write('{:s}\n'.format('%s/%s.jpg' % (img_dir, img_name)))
        f.write('{:d}\n'.format(len(results)))
        for b in results[1]:
            x1, y1, x2, y2, s = b[0], b[1], b[2], b[3], b[4]
            f.write('{:.1f} {:.1f} {:.1f} {:.1f} {:.3f}\n'.format(x1, y1, (x2 - x1 + 1), (y2 - y1 + 1), s))
        f.close()

    def centerface_decode(self, heat, wh, kps, reg=None, opt_k=100, topk_inds=None):
        """
        Decode detection bbox
        """
        batch, _, _, width = wh.shape

        num_joints = kps.shape[1] // 2

        scores = heat
        inds = topk_inds
        ys_int = (topk_inds / width).astype(np.int32).astype(np.float32)
        xs_int = (topk_inds % width).astype(np.int32).astype(np.float32)

        reg = reg.reshape(batch, 2, -1)
        reg_tmp = np.zeros((batch, 2, opt_k), dtype=np.float32)
        for i in range(batch):
            reg_tmp[i, 0, :] = reg[i, 0, inds[i]]
            reg_tmp[i, 1, :] = reg[i, 1, inds[i]]
        reg = reg_tmp.transpose(0, 2, 1)

        if reg is not None:
            xs = xs_int.reshape(batch, opt_k, 1) + reg[:, :, 0:1]
            ys = ys_int.reshape(batch, opt_k, 1) + reg[:, :, 1:2]
        else:
            xs = xs_int.reshape(batch, opt_k, 1) + 0.5
            ys = ys_int.reshape(batch, opt_k, 1) + 0.5

        wh = wh.reshape(batch, 2, -1)
        wh_tmp = np.zeros((batch, 2, opt_k), dtype=np.float32)
        for i in range(batch):
            wh_tmp[i, 0, :] = wh[i, 0, inds[i]]
            wh_tmp[i, 1, :] = wh[i, 1, inds[i]]

        wh = wh_tmp.transpose(0, 2, 1)
        wh = np.exp(wh) * 4.  # Recover the down ratio(4) during data preprocessing
        scores = scores.reshape(batch, opt_k, 1)
        bboxes = np.concatenate([xs - wh[..., 0:1] / 2, ys - wh[..., 1:2] / 2, xs + wh[..., 0:1] / 2,
                                 ys + wh[..., 1:2] / 2], axis=2)

        clses = np.zeros((batch, opt_k, 1), dtype=np.float32)
        kps = np.zeros((batch, opt_k, num_joints * 2), dtype=np.float32)
        detections = np.concatenate([bboxes, scores, kps, clses], axis=2)  # box:4+score:1+kpoints:10+class:1=16
        return detections

    def get_eval_result(self):
        """
        evaluation method.
        """
        save_path = self.save_path
        print_pred = save_path
        pred_evaluation = get_preds(save_path)
        norm_score(pred_evaluation)
        facebox_list, event_list, file_list, hard_gt_list, medium_gt_list, easy_gt_list = get_gt_boxes(self.gt_path)
        event_num = len(event_list)
        thresh_num = 1000
        setting_gts = [easy_gt_list, medium_gt_list, hard_gt_list]

        aps = []
        for setting_id in range(3):
            # different setting
            gt_list = setting_gts[setting_id]
            count_face = 0
            pr_curve = np.zeros((thresh_num, 2)).astype('float')
            # [hard, medium, easy]
            pbar = range(event_num)
            error_count = 0
            for i in pbar:
                event_name = str(event_list[i][0][0])
                img_list = file_list[i][0]
                pred_list = pred_evaluation[event_name]
                sub_gt_list = gt_list[i][0]
                gt_bbx_list = facebox_list[i][0]

                for j, _ in enumerate(img_list):
                    try:
                        pred_info = pred_list[str(img_list[j][0][0])]
                    except KeyError:
                        error_count += 1
                        continue

                    gt_boxes = gt_bbx_list[j][0].astype('float')
                    keep_index = sub_gt_list[j][0]
                    count_face += len(keep_index)
                    if gt_boxes.size == 0 or pred_info.size == 0:
                        continue
                    ignore = np.zeros(gt_boxes.shape[0])
                    if keep_index.size != 0:
                        ignore[keep_index - 1] = 1
                    pred_recall, proposal_list = image_eval(pred_info, gt_boxes, ignore, self.iou_thresh)

                    pr_curve += img_pr_info(thresh_num, pred_info, proposal_list, pred_recall)

            pr_curve = dataset_pr_info(thresh_num, pr_curve, count_face)

            propose = pr_curve[:, 0]
            recall = pr_curve[:, 1]

            ap = voc_ap(recall, propose)
            aps.append(ap)

        print("==================== Results = ====================", print_pred)
        print("Easy   Val AP: {}".format(aps[0]))
        print("Medium Val AP: {}".format(aps[1]))
        print("Hard   Val AP: {}".format(aps[2]))
        print("=================================================")


def transform_preds(coords, center, scale, output_size):
    """
    Transform target coords
    """
    target_coords = np.zeros(coords.shape)
    trans = get_affine_transform(center, scale, 0, output_size, inv=1)
    for p in range(coords.shape[0]):
        target_coords[p, 0:2] = affine_transform(coords[p, 0:2], trans)
    return target_coords


def multi_pose_post_process(dets, c, s, h, w):
    """
    Multi pose post process
    dets_result: 4 + score:1 + kpoints:10 + class:1 = 16
    dets: batch x max_dets x 40
    return list of 39 in image coord
    """
    ret = []
    for i in range(dets.shape[0]):
        bbox = transform_preds(dets[i, :, :4].reshape(-1, 2), c[i], s[i], (w, h))
        pts = transform_preds(dets[i, :, 5:15].reshape(-1, 2), c[i], s[i], (w, h))
        top_preds = np.concatenate([bbox.reshape(-1, 4), dets[i, :, 4:5], pts.reshape(-1, 10)],
                                   axis=1).astype(np.float32).tolist()
        ret.append({np.ones(1, dtype=np.int32)[0]: top_preds})
    return ret


def get_gt_boxes(gt_dir):
    """ gt dir: (wider_face_val.mat, wider_easy_val.mat, wider_medium_val.mat, wider_hard_val.mat)"""

    gt_mat = loadmat(os.path.join(gt_dir, 'wider_face_val.mat'))  # you own ground_truth name
    hard_mat = loadmat(os.path.join(gt_dir, 'wider_hard_val.mat'))
    medium_mat = loadmat(os.path.join(gt_dir, 'wider_medium_val.mat'))
    easy_mat = loadmat(os.path.join(gt_dir, 'wider_easy_val.mat'))

    facebox_list = gt_mat['face_bbx_list']
    event_list = gt_mat['event_list']
    file_list = gt_mat['file_list']

    hard_gt_list = hard_mat['gt_list']
    medium_gt_list = medium_mat['gt_list']
    easy_gt_list = easy_mat['gt_list']

    return facebox_list, event_list, file_list, hard_gt_list, medium_gt_list, easy_gt_list


def get_gt_boxes_from_txt(gt_path, cache_dir):
    """
    Get gt boxes from binary txt file.
    """
    cache_file = os.path.join(cache_dir, 'gt_cache.pkl')
    if os.path.exists(cache_file):
        f = open(cache_file, 'rb')
        boxes = pickle.load(f)
        f.close()
        return boxes

    f = open(gt_path, 'r')
    state = 0
    lines = f.readlines()
    lines = list(map(lambda x: x.rstrip('\r\n'), lines))
    boxes = {}
    f.close()
    current_boxes = []
    current_name = None
    for line in lines:
        if state == 0 and '--' in line:
            state = 1
            current_name = line
            continue
        if state == 1:
            state = 2
            continue

        if state == 2 and '--' in line:
            state = 1
            boxes[current_name] = np.array(current_boxes).astype('float32')
            current_name = line
            current_boxes = []
            continue

        if state == 2:
            box = [float(x) for x in line.split(' ')[:4]]
            current_boxes.append(box)
            continue

    f = open(cache_file, 'wb')
    pickle.dump(boxes, f)
    f.close()
    return boxes


def read_pred_file(filepath):
    """read_pred_file"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
        img_file = lines[0].rstrip('\n\r')
        lines = lines[2:]

    boxes = np.array(list(map(lambda x: [float(a) for a in x.rstrip('\r\n').split(' ')], lines))).astype('float')
    return img_file.split('/')[-1], boxes


def get_preds(pred_dir):
    """Get preds"""
    events = os.listdir(pred_dir)
    boxes = dict()
    pbar = events
    for event in pbar:
        event_dir = os.path.join(pred_dir, event)
        event_images = os.listdir(event_dir)
        current_event = dict()
        for imgtxt in event_images:
            imgname, box = read_pred_file(os.path.join(event_dir, imgtxt))
            current_event[imgname.rstrip('.jpg')] = box
        boxes[event] = current_event
    return boxes


def norm_score(pred_norm):
    """ norm score
    pred_norm {key: [[x1,y1,x2,y2,s]]}
    """
    max_score = 0
    min_score = 1

    for _, k in pred_norm.items():
        for _, v in k.items():
            if v.size == 0:
                continue
            min_v = np.min(v[:, -1])
            max_v = np.max(v[:, -1])
            max_score = max(max_v, max_score)
            min_score = min(min_v, min_score)

    diff = max_score - min_score
    for _, k in pred_norm.items():
        for _, v in k.items():
            if v.size == 0:
                continue
            v[:, -1] = (v[:, -1] - min_score) / diff


def image_eval(pred_eval, gt, ignore, iou_thresh):
    """ single image evaluation
    pred_eval: Nx5
    gt: Nx4
    ignore:
    """
    pred_t = pred_eval.copy()
    gt_t = gt.copy()
    pred_recall = np.zeros(pred_t.shape[0])
    recall_list = np.zeros(gt_t.shape[0])
    proposal_list = np.ones(pred_t.shape[0])

    pred_t[:, 2] = pred_t[:, 2] + pred_t[:, 0]
    pred_t[:, 3] = pred_t[:, 3] + pred_t[:, 1]
    gt_t[:, 2] = gt_t[:, 2] + gt_t[:, 0]
    gt_t[:, 3] = gt_t[:, 3] + gt_t[:, 1]

    overlaps = bbox_overlaps(pred_t[:, :4], gt_t)

    for h in range(pred_t.shape[0]):

        gt_overlap = overlaps[h]
        max_overlap, max_idx = gt_overlap.max(), gt_overlap.argmax()
        if max_overlap >= iou_thresh:
            if ignore[max_idx] == 0:
                recall_list[max_idx] = -1
                proposal_list[h] = -1
            elif recall_list[max_idx] == 0:
                recall_list[max_idx] = 1

        r_keep_index = np.where(recall_list == 1)[0]
        pred_recall[h] = len(r_keep_index)
    return pred_recall, proposal_list


def img_pr_info(thresh_num, pred_info, proposal_list, pred_recall):
    """
    Image pr info
    """
    pr_info = np.zeros((thresh_num, 2)).astype('float')
    for t in range(thresh_num):

        thresh = 1 - (t + 1) / thresh_num
        r_index = np.where(pred_info[:, 4] >= thresh)[0]
        if r_index.size == 0:
            pr_info[t, 0] = 0
            pr_info[t, 1] = 0
        else:
            r_index = r_index[-1]
            p_index = np.where(proposal_list[:r_index + 1] == 1)[0]
            pr_info[t, 0] = len(p_index)
            pr_info[t, 1] = pred_recall[r_index]
    return pr_info


def dataset_pr_info(thresh_num, pr_curve, count_face):
    """Get dataset_pr_info"""
    pr_curve_t = np.zeros((thresh_num, 2))
    for i in range(thresh_num):
        pr_curve_t[i, 0] = pr_curve[i, 1] / pr_curve[i, 0]
        pr_curve_t[i, 1] = pr_curve[i, 1] / count_face
    return pr_curve_t


def voc_ap(rec, prec):
    """
    Voc ap calculation
    """
    # correct AP calculation
    # first append sentinel values at the end
    mrec = np.concatenate(([0.], rec, [1.]))
    mpre = np.concatenate(([0.], prec, [0.]))

    # compute the precision envelope
    for i in range(mpre.size - 1, 0, -1):
        mpre[i - 1] = np.maximum(mpre[i - 1], mpre[i])

    # to calculate area under PR curve, look for points
    # where X axis (recall) changes value
    i = np.where(mrec[1:] != mrec[:-1])[0]

    # and sum (\Delta recall) * prec
    ap = np.sum((mrec[i + 1] - mrec[i]) * mpre[i + 1])
    return ap
