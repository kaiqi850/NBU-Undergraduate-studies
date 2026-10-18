# Copyright 2021 Huawei Technologies Co., Ltd
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
""" MindSpore Vision Classification infer script. TODO: @liujunyu add infer after imagenet dataset finished. """

# import os
# import numpy as np
#
# import mindspore as ms
# from mindspore import Tensor, context, load_checkpoint, load_param_into_net
# from mindspore.train import Model
#
# from mindvision.classification.models.builder import build_classifier
# from mindvision.classification.utils.image import get_image_list, preprocess, show_result
# from mindvision.engine.utils.config import Config, parse_args
# from mindvision.io import images as im
#
#
# def main(pargs):
#     config = Config(pargs.config)
#
#     # set config context
#     context.set_context(**config.context)
#
#     # set network
#     network = build_classifier(config.model)
#
#     # load pertain model
#     param_dict = load_checkpoint(config.infer.pretrained_model)
#     load_param_into_net(network, param_dict)
#
#     # init the whole Model
#     model = Model(network)
#
#     # begin to infer
#     image_list = get_image_list(config.infer.image_path)
#     batch_input_list = []
#     img_name_list = []
#     cnt = 0
#
#     print(f'[Start infer `{config.model_name}`]')
#     print("=" * 80)
#     for idx, image_path in enumerate(image_list):
#         # image input shape
#         if config.infer.image_shape[0] == 1:
#             image = im.imread(image_path, flag="grayscale")
#         else:
#             image = im.imread(image_path, flag="color")
#         image = preprocess(image, config)
#         batch_input_list.append(image)
#         img_name = image_path.split("/")[-1]
#         img_name_list.append(img_name)
#         cnt += 1
#         if cnt % config.infer.batch_size == 0 or (idx + 1) == len(image_list):
#             if config.infer.image_shape[0] == 1:
#                 batch_input_list = np.expand_dims(
#                     np.array(batch_input_list), axis=1)
#             else:
#                 batch_input_list = np.transpose(
#                     np.array(batch_input_list), (0, 3, 1, 2))  # (224,224,3) =>(3,224,224)
#
#             batch_input_list = Tensor(batch_input_list, ms.float32)
#             batch_outputs = model.predict(batch_input_list)
#             index = np.argmax(batch_outputs.asnumpy(), axis=1)
#             for i, img_name in enumerate(img_name_list):
#                 res_index = index[i]
#                 label = labels[int(res_index)]
#                 out_file = os.path.join(config.infer.output_dir, img_name)
#                 result = {}
#                 result[label] = batch_outputs[i][int(res_index)]
#                 show_result(image_list[i], result, out_file=out_file)
#             batch_input_list = []
#             img_name_list = []
#     print("=" * 80)
#     print(f'End of infer {config.model_name}.')
#
#
# if __name__ == '__main__':
#     args = parse_args()
#     main(args)
