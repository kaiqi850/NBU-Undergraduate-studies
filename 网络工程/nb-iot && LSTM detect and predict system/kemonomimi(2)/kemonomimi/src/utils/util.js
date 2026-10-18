/**
 * 仅添加模型
 * 
 * @param {String} path 导入的模型路径
 * @param {object}  position 模型的xyz轴坐标，输入参数:{x,y,z}
 * @param {object} scale 模型的xyz轴缩放倍率，输入参数:{x,y,z}
 * @param {object} rotation 模型沿xyz轴的旋转角度,输入参数:{x,y,z},计算公式：Math.PI,用pi来表示弧度
 * @param {GLTFLoader} loader GLTF加载器`实例`
 * @param {THREE.Scene} scene 往场景中添加Group的`实例`
 * @param {TransformControl} TransformControls 用于添加可拖拽的xyz轴的`对象`，参数可以为`NULL`
 * @param {THREE.PerspectiveCamera} camera 摄像机的`实例`，用于添加xyz轴，只有TransformControls不为NULL时有效
 * @param {Controls} controls 可移动摄像机的`实例`，用于添加xyz轴，只有TransformControls不为NULL时有效
 * @param {THREE.WebGLRenderer} renderer 渲染器的`实例`，用于添加xyz轴，只有TransformControls不为NULL时有效
 */
function addModel(
    path,
    position, scale, rotation,
    loader, scene,
    TransformControls, camera, controls, renderer
) {
    loader.load(
        path,
        gltf => {
            // 设置模型的坐标、缩放比例、旋转角度
            gltf.scene.position.set(position.x, position.y, position.z);
            gltf.scene.scale.set(scale.x, scale.y, scale.z);
            gltf.scene.rotation.set(rotation.x, rotation.y, rotation.z);

            // 添加场景
            scene.add(gltf.scene);

            // 添加可拖拽轴
            // if (TransformControls != null) {
            //     // 创建TransformControls，用于模型的xyz轴移动
            //     const transformControls = new TransformControls(camera, renderer.domElement);
            //     // 将TransformControls附加到模型上面
            //     transformControls.attach(gltf.scene);
            //     scene.add(transformControls);

            //     // 拖拽模型时关闭摄像头的移动
            //     transformControls.addEventListener('mouseDown', () => controls.enabled = false);
            //     transformControls.addEventListener('mouseUp', () => controls.enabled = true);

            //     // 拖拽模型时输出被拖拽模型的坐标
            //     transformControls.addEventListener('objectChange', () => {
            //         const position = transformControls.object.position;
            //         console.log(`Model Position - X: ${position.x.toFixed(3)}, Y: ${position.y.toFixed(3)}, Z: ${position.z.toFixed(3)}`);
            //     });
            // }
        }
    )
}

/**
 * 添加模型，并且把标签和模型绑定在一起
 * 
 * @param {String} path 导入的模型路径
 * @param {object}  position 模型的xyz轴坐标，输入参数:{x,y,z}
 * @param {object} scale 模型的xyz轴缩放倍率，输入参数:{x,y,z}
 * @param {object} rotation 模型沿xyz轴的旋转角度,输入参数:{x,y,z},计算公式：Math.PI,用pi来表示弧度
 * @param {String} ElementId HTML元素的id，用于获取到元素并转换为threejs模型
 * @param {object} label_position 标签相对于模型的坐标
 * @param {object} label_scale 标签的缩放倍率，标签缩放倍率会在模型缩放倍率基础上调整
 * @param {GLTFLoader} loader GLTF加载器`实例`
 * @param {CSS3DSprite} CSS3DSprite CSS3标签渲染器`对象`
 * @param {THREE.Group} group 用于将模型和标签绑定在一个场景中的`实例`
 * @param {THREE.Scene} scene 往场景中添加Group的`实例`
 * @param {TransformControl} TransformControls 用于添加可拖拽的xyz轴的`对象`，参数可以为`NULL`
 * @param {THREE.PerspectiveCamera} camera 摄像机的`实例`，用于添加xyz轴，只有TransformControls不为NULL时有效
 * @param {Controls} controls 可移动摄像机的`实例`，用于添加xyz轴，只有TransformControls不为NULL时有效
 * @param {THREE.WebGLRenderer} renderer 渲染器的`实例`，用于添加xyz轴，只有TransformControls不为NULL时有效
 * @param animationCallBack 调用模型的动画，由于模型是异步加载，使用cb来进行调用
 * @param actionId 动画模型的id，用于控制特定模型的开关
  */
function addModelAndLable(
    path,
    position, scale, rotation,
    ElementId,
    label_position, label_scale,
    loader,
    CSS3DSprite,
    group, scene,
    TransformControls, camera, controls, renderer,
    animationCallBack, actionId) {
    loader.load(
        path,
        gltf => {
            // 设置模型的坐标、缩放比例、旋转角度
            gltf.scene.position.set(position.x, position.y, position.z);
            gltf.scene.scale.set(scale.x, scale.y, scale.z);
            gltf.scene.rotation.set(rotation.x, rotation.y, rotation.z);

            // 创建标签
            const div = document.getElementById(ElementId);
            div.style.pointerEvents = 'none';
            const css3Obj = new CSS3DSprite(div);

            // 设置标签的坐标和缩放比率
            css3Obj.position.set(label_position.x, label_position.y, label_position.z)
            css3Obj.scale.set(label_scale.x, label_scale.y, label_scale.z);

            // 往场景中添加组
            group = gltf.scene;
            group.add(css3Obj);
            scene.add(group);

            // if (TransformControls != null) {
            //     // 创建TransformControls，用于模型的xyz轴移动
            //     const transformControls = new TransformControls(camera, renderer.domElement);
            //     // 将TransformControls附加到模型上面
            //     transformControls.attach(gltf.scene);
            //     scene.add(transformControls);

            //     // 拖拽模型时关闭摄像头的移动
            //     transformControls.addEventListener('mouseDown', () => controls.enabled = false);
            //     transformControls.addEventListener('mouseUp', () => controls.enabled = true);

            //     // 拖拽模型时输出被拖拽模型的坐标
            //     transformControls.addEventListener('objectChange', () => {
            //         const position = transformControls.object.position;
            //         console.log(`Model Position - X: ${position.x.toFixed(3)}, Y: ${position.y.toFixed(3)}, Z: ${position.z.toFixed(3)}`);
            //     });
            // }

            if (animationCallBack != null) {
                animationCallBack(gltf, actionId);
            }
        }
    )
}

export { addModelAndLable, addModel };